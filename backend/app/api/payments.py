# backend/app/api/payments.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database.connection import db
from app.database.models import Payment, Invoice
from datetime import datetime
import stripe
import os

payments_bp = Blueprint('payments', __name__)

# Stripe configuration (test mode for hackathon)
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_4eC39HqLyjWDarjtT1zdp7dc')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', 'pk_test_TYooMQauvdEDq54NiTphI7jx')

@payments_bp.route('/', methods=['GET'])
@jwt_required()
def get_payments():
    """Get all payments (admin) or customer's payments"""
    try:
        current_user = get_jwt_identity()
        
        if current_user['role'] == 'admin':
            # Admin sees all payments
            payments = Payment.query.all()
        else:
            # Customer sees only payments for their invoices
            customer_invoices = Invoice.query.filter_by(customer_id=current_user['id']).all()
            invoice_ids = [inv.id for inv in customer_invoices]
            payments = Payment.query.filter(Payment.invoice_id.in_(invoice_ids)).all()
        
        return jsonify([p.to_dict() for p in payments]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/invoice/<int:invoice_id>', methods=['GET'])
@jwt_required()
def get_invoice_payments(invoice_id):
    """Get payments for specific invoice"""
    try:
        invoice = Invoice.query.get_or_404(invoice_id)
        current_user = get_jwt_identity()
        
        # Check permission
        if current_user['role'] != 'admin' and invoice.customer_id != current_user['id']:
            return jsonify({'error': 'Access denied'}), 403
        
        payments = Payment.query.filter_by(invoice_id=invoice_id).all()
        
        return jsonify({
            'invoice_id': invoice_id,
            'invoice_amount': invoice.amount,
            'total_paid': sum(p.amount for p in payments),
            'balance': invoice.amount - sum(p.amount for p in payments),
            'payments': [p.to_dict() for p in payments]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/create-payment-intent', methods=['POST'])
@jwt_required()
def create_payment_intent():
    """Create Stripe payment intent"""
    try:
        data = request.get_json()
        
        if not data.get('invoice_id') or not data.get('amount'):
            return jsonify({'error': 'invoice_id and amount are required'}), 400
        
        invoice = Invoice.query.get_or_404(data['invoice_id'])
        current_user = get_jwt_identity()
        
        # Verify customer owns the invoice
        if current_user['role'] != 'admin' and invoice.customer_id != current_user['id']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Create Stripe payment intent
        intent = stripe.PaymentIntent.create(
            amount=int(data['amount'] * 100),  # Convert to cents
            currency='usd',
            metadata={
                'invoice_id': str(invoice.id),
                'customer_id': str(current_user['id']),
                'invoice_number': invoice.invoice_number
            },
            description=f"Payment for invoice {invoice.invoice_number}"
        )
        
        return jsonify({
            'client_secret': intent.client_secret,
            'publishable_key': STRIPE_PUBLISHABLE_KEY,
            'amount': data['amount'],
            'invoice': invoice.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/record-payment', methods=['POST'])
@jwt_required()
def record_payment():
    """Record a payment (manual or after Stripe webhook)"""
    try:
        data = request.get_json()
        current_user = get_jwt_identity()
        
        if current_user['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        required_fields = ['invoice_id', 'amount', 'payment_method']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        invoice = Invoice.query.get_or_404(data['invoice_id'])
        
        # Create payment record
        payment = Payment(
            invoice_id=data['invoice_id'],
            amount=data['amount'],
            payment_method=data['payment_method'],
            transaction_id=data.get('transaction_id'),
            status='completed'
        )
        
        db.session.add(payment)
        
        # Update invoice status based on total paid
        total_paid = sum(p.amount for p in invoice.payments) + data['amount']
        
        if total_paid >= invoice.amount:
            invoice.status = 'paid'
        elif total_paid > 0:
            invoice.status = 'partial'
        else:
            invoice.status = 'unpaid'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Payment recorded successfully',
            'payment': payment.to_dict(),
            'invoice': invoice.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    try:
        payload = request.get_data(as_text=True)
        sig_header = request.headers.get('Stripe-Signature')
        
        # For hackathon, we'll simulate webhook
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
        
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            
            # Extract metadata
            invoice_id = payment_intent['metadata'].get('invoice_id')
            amount = payment_intent['amount'] / 100  # Convert from cents
            
            if invoice_id:
                # Record the payment
                invoice = Invoice.query.get(int(invoice_id))
                if invoice:
                    payment = Payment(
                        invoice_id=invoice.id,
                        amount=amount,
                        payment_method='stripe',
                        transaction_id=payment_intent['id'],
                        status='completed'
                    )
                    
                    db.session.add(payment)
                    
                    # Update invoice status
                    total_paid = sum(p.amount for p in invoice.payments) + amount
                    if total_paid >= invoice.amount:
                        invoice.status = 'paid'
                    elif total_paid > 0:
                        invoice.status = 'partial'
                    
                    db.session.commit()
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/test-stripe', methods=['GET'])
def test_stripe():
    """Test Stripe connection (for hackathon demo)"""
    return jsonify({
        'status': 'Stripe integration ready',
        'mode': 'test',
        'publishable_key': STRIPE_PUBLISHABLE_KEY,
        'note': 'For demo, use card: 4242 4242 4242 4242'
    })