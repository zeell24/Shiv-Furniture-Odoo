# backend/app/api/payments.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database.connection import get_db
from app.database.models import payment_to_dict, invoice_to_dict, oid
from datetime import datetime
import stripe
import os
import json

payments_bp = Blueprint('payments', __name__)

stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_4eC39HqLyjWDarjtT1zdp7dc')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', 'pk_test_TYooMQauvdEDq54NiTphI7jx')


@payments_bp.route('/', methods=['GET'])
@jwt_required()
def get_payments():
    try:
        current_user = get_jwt_identity()
        db = get_db()
        if current_user['role'] == 'admin':
            cursor = db.payments.find({})
        else:
            inv_ids = [inv['_id'] for inv in db.invoices.find({'customer_id': oid(current_user['id'])})]
            cursor = db.payments.find({'invoice_id': {'$in': inv_ids}})
        out = []
        for p in cursor:
            inv = db.invoices.find_one({'_id': p.get('invoice_id')})
            out.append(payment_to_dict(p, invoice_number=inv.get('invoice_number') if inv else None))
        return jsonify(out), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/invoice/<invoice_id>', methods=['GET'])
@jwt_required()
def get_invoice_payments(invoice_id):
    try:
        db = get_db()
        inv = db.invoices.find_one({'_id': oid(invoice_id)})
        if not inv:
            return jsonify({'error': 'Invoice not found'}), 404
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin' and str(inv.get('customer_id')) != current_user['id']:
            return jsonify({'error': 'Access denied'}), 403

        payments = list(db.payments.find({'invoice_id': inv['_id']}))
        total_paid = sum(p['amount'] for p in payments)
        out = [payment_to_dict(p, invoice_number=inv.get('invoice_number')) for p in payments]
        return jsonify({
            'invoice_id': str(inv['_id']),
            'invoice_amount': inv.get('amount', 0),
            'total_paid': total_paid,
            'balance': inv.get('amount', 0) - total_paid,
            'payments': out
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/create-payment-intent', methods=['POST'])
@jwt_required()
def create_payment_intent():
    try:
        data = request.get_json()
        if not data.get('invoice_id') or not data.get('amount'):
            return jsonify({'error': 'invoice_id and amount are required'}), 400

        db = get_db()
        inv = db.invoices.find_one({'_id': oid(data['invoice_id'])})
        if not inv:
            return jsonify({'error': 'Invoice not found'}), 404
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin' and str(inv.get('customer_id')) != current_user['id']:
            return jsonify({'error': 'Access denied'}), 403

        intent = stripe.PaymentIntent.create(
            amount=int(data['amount'] * 100),
            currency='usd',
            metadata={
                'invoice_id': str(inv['_id']),
                'customer_id': str(current_user['id']),
                'invoice_number': inv.get('invoice_number', '')
            },
            description=f"Payment for invoice {inv.get('invoice_number', '')}"
        )
        paid = sum(p['amount'] for p in db.payments.find({'invoice_id': inv['_id']}))
        cust = db.users.find_one({'_id': inv.get('customer_id')})
        return jsonify({
            'client_secret': intent.client_secret,
            'publishable_key': STRIPE_PUBLISHABLE_KEY,
            'amount': data['amount'],
            'invoice': invoice_to_dict(inv, customer_email=cust.get('email') if cust else None, paid_amount=paid)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/record-payment', methods=['POST'])
@jwt_required()
def record_payment():
    try:
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        data = request.get_json()
        for f in ['invoice_id', 'amount', 'payment_method']:
            if f not in data:
                return jsonify({'error': f'{f} is required'}), 400

        db = get_db()
        inv = db.invoices.find_one({'_id': oid(data['invoice_id'])})
        if not inv:
            return jsonify({'error': 'Invoice not found'}), 404

        doc = {
            'invoice_id': inv['_id'],
            'amount': float(data['amount']),
            'payment_method': data['payment_method'],
            'transaction_id': data.get('transaction_id'),
            'status': 'completed',
            'payment_date': datetime.utcnow(),
            'created_at': datetime.utcnow()
        }
        db.payments.insert_one(doc)
        total_paid = sum(p['amount'] for p in db.payments.find({'invoice_id': inv['_id']}))
        status = 'paid' if total_paid >= inv.get('amount', 0) else ('partial' if total_paid > 0 else 'unpaid')
        db.invoices.update_one({'_id': inv['_id']}, {'$set': {'status': status}})
        inv = db.invoices.find_one({'_id': inv['_id']})
        paid = sum(p['amount'] for p in db.payments.find({'invoice_id': inv['_id']}))
        cust = db.users.find_one({'_id': inv.get('customer_id')})
        return jsonify({
            'message': 'Payment recorded successfully',
            'payment': payment_to_dict(doc, invoice_number=inv.get('invoice_number')),
            'invoice': invoice_to_dict(inv, customer_email=cust.get('email') if cust else None, paid_amount=paid)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    try:
        payload = request.get_data(as_text=True)
        sig_header = request.headers.get('Stripe-Signature')
        event = json.loads(payload)
        if isinstance(event, dict) and event.get('type') == 'payment_intent.succeeded':
            payment_intent = event.get('data', {}).get('object', {})
            invoice_id = payment_intent.get('metadata', {}).get('invoice_id')
            amount = payment_intent.get('amount', 0) / 100
            if invoice_id:
                db = get_db()
                inv = db.invoices.find_one({'_id': oid(invoice_id)})
                if inv:
                    db.payments.insert_one({
                        'invoice_id': inv['_id'],
                        'amount': amount,
                        'payment_method': 'stripe',
                        'transaction_id': payment_intent.get('id'),
                        'status': 'completed',
                        'payment_date': datetime.utcnow(),
                        'created_at': datetime.utcnow()
                    })
                    total_paid = sum(p['amount'] for p in db.payments.find({'invoice_id': inv['_id']}))
                    status = 'paid' if total_paid >= inv.get('amount', 0) else 'partial'
                    db.invoices.update_one({'_id': inv['_id']}, {'$set': {'status': status}})
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/test-stripe', methods=['GET'])
def test_stripe():
    return jsonify({
        'status': 'Stripe integration ready',
        'mode': 'test',
        'publishable_key': STRIPE_PUBLISHABLE_KEY,
        'note': 'For demo, use card: 4242 4242 4242 4242'
    })
