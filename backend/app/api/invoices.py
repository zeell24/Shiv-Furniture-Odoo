# backend/app/api/invoices.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database.connection import db
from app.database.models import Invoice, Payment, User
from datetime import datetime
import random
import string

invoices_bp = Blueprint('invoices', __name__)

def generate_invoice_number():
    """Generate unique invoice number: INV-YYYYMMDD-XXXX"""
    date_str = datetime.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.digits, k=4))
    return f"INV-{date_str}-{random_str}"

@invoices_bp.route('/', methods=['GET'])
@jwt_required()
def get_invoices():
    """Get all invoices (admin) or customer's invoices"""
    try:
        current_user = get_jwt_identity()
        
        if current_user['role'] == 'admin':
            # Admin sees all invoices
            invoices = Invoice.query.all()
        else:
            # Customer sees only their invoices
            invoices = Invoice.query.filter_by(customer_id=current_user['id']).all()
        
        return jsonify([inv.to_dict() for inv in invoices]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@invoices_bp.route('/<int:invoice_id>', methods=['GET'])
@jwt_required()
def get_invoice(invoice_id):
    """Get specific invoice"""
    try:
        invoice = Invoice.query.get_or_404(invoice_id)
        current_user = get_jwt_identity()
        
        # Check permission: admin or invoice owner
        if current_user['role'] != 'admin' and invoice.customer_id != current_user['id']:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify(invoice.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@invoices_bp.route('/', methods=['POST'])
@jwt_required()
def create_invoice():
    """Create a new invoice (admin only)"""
    try:
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['customer_id', 'amount']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if customer exists
        customer = User.query.get(data['customer_id'])
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Generate invoice number
        invoice_number = generate_invoice_number()
        
        # Parse due date if provided
        due_date = None
        if data.get('due_date'):
            due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        
        # Create invoice
        new_invoice = Invoice(
            invoice_number=invoice_number,
            customer_id=data['customer_id'],
            amount=data['amount'],
            due_date=due_date,
            status='unpaid'
        )
        
        db.session.add(new_invoice)
        db.session.commit()
        
        return jsonify({
            'message': 'Invoice created successfully',
            'invoice': new_invoice.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@invoices_bp.route('/<int:invoice_id>/status', methods=['PUT'])
@jwt_required()
def update_invoice_status(invoice_id):
    """Update invoice status (admin only)"""
    try:
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        invoice = Invoice.query.get_or_404(invoice_id)
        data = request.get_json()
        
        if 'status' not in data:
            return jsonify({'error': 'status is required'}), 400
        
        if data['status'] not in ['unpaid', 'partial', 'paid']:
            return jsonify({'error': "status must be 'unpaid', 'partial', or 'paid'"}), 400
        
        invoice.status = data['status']
        db.session.commit()
        
        return jsonify({
            'message': 'Invoice status updated',
            'invoice': invoice.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@invoices_bp.route('/customer/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_customer_invoices(customer_id):
    """Get invoices for specific customer (admin only)"""
    try:
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        invoices = Invoice.query.filter_by(customer_id=customer_id).all()
        
        # Calculate totals
        total_amount = sum(inv.amount for inv in invoices)
        total_paid = sum(
            sum(payment.amount for payment in inv.payments)
            for inv in invoices
        )
        
        return jsonify({
            'customer_id': customer_id,
            'total_invoices': len(invoices),
            'total_amount': total_amount,
            'total_paid': total_paid,
            'total_balance': total_amount - total_paid,
            'invoices': [inv.to_dict() for inv in invoices]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500