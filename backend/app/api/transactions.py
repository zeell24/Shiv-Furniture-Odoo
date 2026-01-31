# backend/app/api/transactions.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database.connection import db
from app.database.models import Transaction, CostCenter, Product
from datetime import datetime

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/', methods=['GET'])
@jwt_required()
def get_transactions():
    """Get all transactions with optional filters"""
    try:
        # Get query parameters
        transaction_type = request.args.get('type')  # 'purchase' or 'sale'
        cost_center_id = request.args.get('cost_center_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query
        query = Transaction.query
        
        if transaction_type:
            query = query.filter(Transaction.type == transaction_type)
        
        if cost_center_id:
            query = query.filter(Transaction.cost_center_id == cost_center_id)
        
        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Transaction.transaction_date >= start)
        
        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Transaction.transaction_date <= end)
        
        # Order by date (newest first)
        transactions = query.order_by(Transaction.transaction_date.desc()).all()
        
        return jsonify([t.to_dict() for t in transactions]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transactions_bp.route('/<int:transaction_id>', methods=['GET'])
@jwt_required()
def get_transaction(transaction_id):
    """Get specific transaction"""
    try:
        transaction = Transaction.query.get_or_404(transaction_id)
        return jsonify(transaction.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transactions_bp.route('/', methods=['POST'])
@jwt_required()
def create_transaction():
    """Create a new transaction"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['type', 'amount', 'cost_center_id', 'transaction_date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate transaction type
        if data['type'] not in ['purchase', 'sale']:
            return jsonify({'error': "type must be 'purchase' or 'sale'"}), 400
        
        # Check if cost center exists
        cost_center = CostCenter.query.get(data['cost_center_id'])
        if not cost_center:
            return jsonify({'error': 'Cost center not found'}), 404
        
        # Check if product exists (if provided)
        if data.get('product_id'):
            product = Product.query.get(data['product_id'])
            if not product:
                return jsonify({'error': 'Product not found'}), 404
        
        # Parse date
        transaction_date = datetime.strptime(data['transaction_date'], '%Y-%m-%d').date()
        
        # Normalize status
        status = data.get('status', 'paid')
        if status not in ('paid', 'not_paid', 'partially_paid'):
            status = 'paid'

        # Create transaction
        new_transaction = Transaction(
            type=data['type'],
            amount=data['amount'],
            cost_center_id=data['cost_center_id'],
            product_id=data.get('product_id'),
            quantity=data.get('quantity', 1),
            description=data.get('description', ''),
            transaction_date=transaction_date,
            status=status
        )
        
        db.session.add(new_transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'Transaction created successfully',
            'transaction': new_transaction.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@transactions_bp.route('/<int:transaction_id>', methods=['PUT'])
@jwt_required()
def update_transaction(transaction_id):
    """Update a transaction"""
    try:
        transaction = Transaction.query.get_or_404(transaction_id)
        data = request.get_json()
        
        # Update fields if provided
        if 'type' in data:
            if data['type'] not in ['purchase', 'sale']:
                return jsonify({'error': "type must be 'purchase' or 'sale'"}), 400
            transaction.type = data['type']
        
        if 'amount' in data:
            transaction.amount = data['amount']
        
        if 'cost_center_id' in data:
            # Verify cost center exists
            cost_center = CostCenter.query.get(data['cost_center_id'])
            if not cost_center:
                return jsonify({'error': 'Cost center not found'}), 404
            transaction.cost_center_id = data['cost_center_id']
        
        if 'product_id' in data:
            if data['product_id']:
                product = Product.query.get(data['product_id'])
                if not product:
                    return jsonify({'error': 'Product not found'}), 404
            transaction.product_id = data['product_id']
        
        if 'quantity' in data:
            transaction.quantity = data['quantity']
        
        if 'description' in data:
            transaction.description = data['description']
        
        if 'transaction_date' in data:
            transaction.transaction_date = datetime.strptime(data['transaction_date'], '%Y-%m-%d').date()
        
        if 'status' in data and data['status'] in ('paid', 'not_paid', 'partially_paid'):
            transaction.status = data['status']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Transaction updated successfully',
            'transaction': transaction.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@transactions_bp.route('/<int:transaction_id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(transaction_id):
    """Delete a transaction"""
    try:
        transaction = Transaction.query.get_or_404(transaction_id)
        
        db.session.delete(transaction)
        db.session.commit()
        
        return jsonify({'message': 'Transaction deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@transactions_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_transaction_summary():
    """Get transaction summary for dashboard"""
    try:
        # Total transactions count
        total_transactions = Transaction.query.count()
        
        # Total purchase amount
        total_purchase = db.session.query(db.func.sum(Transaction.amount))\
            .filter(Transaction.type == 'purchase')\
            .scalar() or 0
        
        # Total sales amount
        total_sales = db.session.query(db.func.sum(Transaction.amount))\
            .filter(Transaction.type == 'sale')\
            .scalar() or 0
        
        # Recent transactions (last 10)
        recent_transactions = Transaction.query\
            .order_by(Transaction.transaction_date.desc())\
            .limit(10)\
            .all()
        
        return jsonify({
            'total_transactions': total_transactions,
            'total_purchase': total_purchase,
            'total_sales': total_sales,
            'net_flow': total_sales - total_purchase,
            'recent_transactions': [t.to_dict() for t in recent_transactions]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500