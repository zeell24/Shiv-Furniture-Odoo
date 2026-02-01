# backend/app/api/invoices.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database.connection import get_db
from app.database.models import invoice_to_dict, user_to_dict, oid
from datetime import datetime
import random
import string

invoices_bp = Blueprint('invoices', __name__)


def generate_invoice_number():
    date_str = datetime.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.digits, k=4))
    return f"INV-{date_str}-{random_str}"


@invoices_bp.route('/', methods=['GET'])
@jwt_required()
def get_invoices():
    try:
        current_user = get_jwt_identity()
        db = get_db()
        if current_user['role'] == 'admin':
            cursor = db.invoices.find({})
        else:
            cursor = db.invoices.find({'customer_id': oid(current_user['id'])})
        out = []
        for inv in cursor:
            cust = db.users.find_one({'_id': inv.get('customer_id')})
            paid = sum(p['amount'] for p in db.payments.find({'invoice_id': inv['_id']}))
            out.append(invoice_to_dict(inv, customer_email=cust.get('email') if cust else None, paid_amount=paid))
        return jsonify(out), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@invoices_bp.route('/<id>', methods=['GET'])
@jwt_required()
def get_invoice(id):
    try:
        current_user = get_jwt_identity()
        db = get_db()
        inv = db.invoices.find_one({'_id': oid(id)})
        if not inv:
            return jsonify({'error': 'Invoice not found'}), 404
        if current_user['role'] != 'admin' and str(inv.get('customer_id')) != current_user['id']:
            return jsonify({'error': 'Access denied'}), 403
        cust = db.users.find_one({'_id': inv.get('customer_id')})
        paid = sum(p['amount'] for p in db.payments.find({'invoice_id': inv['_id']}))
        return jsonify(invoice_to_dict(inv, customer_email=cust.get('email') if cust else None, paid_amount=paid)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@invoices_bp.route('/', methods=['POST'])
@jwt_required()
def create_invoice():
    try:
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        data = request.get_json()
        if 'customer_id' not in data or 'amount' not in data:
            return jsonify({'error': 'customer_id and amount are required'}), 400

        db = get_db()
        cust_id = oid(data['customer_id'])
        if not db.users.find_one({'_id': cust_id}):
            return jsonify({'error': 'Customer not found'}), 404

        invoice_number = generate_invoice_number()
        due_date = None
        if data.get('due_date'):
            due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()

        doc = {
            'invoice_number': invoice_number,
            'customer_id': cust_id,
            'amount': float(data['amount']),
            'status': 'unpaid',
            'due_date': due_date,
            'created_at': datetime.utcnow()
        }
        r = db.invoices.insert_one(doc)
        doc['_id'] = r.inserted_id
        cust = db.users.find_one({'_id': cust_id})
        return jsonify({
            'message': 'Invoice created successfully',
            'invoice': invoice_to_dict(doc, customer_email=cust.get('email') if cust else None, paid_amount=0)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@invoices_bp.route('/<id>/status', methods=['PUT'])
@jwt_required()
def update_invoice_status(id):
    try:
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        data = request.get_json()
        if 'status' not in data:
            return jsonify({'error': 'status is required'}), 400
        if data['status'] not in ('unpaid', 'partial', 'paid'):
            return jsonify({'error': "status must be 'unpaid', 'partial', or 'paid'"}), 400

        db = get_db()
        inv = db.invoices.find_one({'_id': oid(id)})
        if not inv:
            return jsonify({'error': 'Invoice not found'}), 404
        db.invoices.update_one({'_id': oid(id)}, {'$set': {'status': data['status']}})
        inv = db.invoices.find_one({'_id': oid(id)})
        paid = sum(p['amount'] for p in db.payments.find({'invoice_id': inv['_id']}))
        cust = db.users.find_one({'_id': inv.get('customer_id')})
        return jsonify({
            'message': 'Invoice status updated',
            'invoice': invoice_to_dict(inv, customer_email=cust.get('email') if cust else None, paid_amount=paid)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@invoices_bp.route('/customer/<customer_id>', methods=['GET'])
@jwt_required()
def get_customer_invoices(customer_id):
    try:
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        db = get_db()
        cid = oid(customer_id)
        invoices = list(db.invoices.find({'customer_id': cid}))
        total_amount = sum(inv.get('amount', 0) for inv in invoices)
        total_paid = 0
        out = []
        for inv in invoices:
            paid = sum(p['amount'] for p in db.payments.find({'invoice_id': inv['_id']}))
            total_paid += paid
            cust = db.users.find_one({'_id': inv.get('customer_id')})
            out.append(invoice_to_dict(inv, customer_email=cust.get('email') if cust else None, paid_amount=paid))
        return jsonify({
            'customer_id': customer_id,
            'total_invoices': len(invoices),
            'total_amount': total_amount,
            'total_paid': total_paid,
            'total_balance': total_amount - total_paid,
            'invoices': out
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
