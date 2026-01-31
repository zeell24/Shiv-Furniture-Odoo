# backend/app/api/budget.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database.connection import db
from app.database.models import Budget, CostCenter, Transaction, MasterBudget
from datetime import datetime, date
from sqlalchemy import and_

budget_bp = Blueprint('budget', __name__)


@budget_bp.route('/master', methods=['GET'])
@jwt_required()
def get_master_budget():
    """Get organization-wide master budget"""
    try:
        mb = MasterBudget.query.first()
        if not mb:
            mb = MasterBudget(amount=1500000)
            db.session.add(mb)
            db.session.commit()
        return jsonify({'amount': mb.amount, 'updated_at': mb.updated_at.isoformat() if mb.updated_at else None}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@budget_bp.route('/master', methods=['PUT'])
@jwt_required()
def update_master_budget():
    """Update master budget (admin revision)"""
    try:
        data = request.get_json()
        if 'amount' not in data:
            return jsonify({'error': 'amount is required'}), 400
        amount = float(data['amount'])
        if amount < 0:
            return jsonify({'error': 'amount must be positive'}), 400

        mb = MasterBudget.query.first()
        if not mb:
            mb = MasterBudget(amount=amount)
            db.session.add(mb)
        else:
            mb.amount = amount
        db.session.commit()
        return jsonify({'message': 'Master budget updated', 'amount': mb.amount}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Helper function for budget calculations
def calculate_budget_utilization(budget):
    """Calculate budget utilization for a specific budget"""
    # Get all transactions for this cost center within budget period
    transactions = Transaction.query.filter(
        and_(
            Transaction.cost_center_id == budget.cost_center_id,
            Transaction.transaction_date >= budget.period_start,
            Transaction.transaction_date <= budget.period_end
        )
    ).all()
    
    total_spent = sum(t.amount for t in transactions)
    
    utilization_percentage = (total_spent / budget.amount * 100) if budget.amount > 0 else 0
    remaining = budget.amount - total_spent
    
    return {
        'budget_amount': budget.amount,
        'actual_spent': total_spent,
        'utilization_percentage': round(utilization_percentage, 2),
        'remaining_balance': remaining,
        'is_over_budget': total_spent > budget.amount
    }

@budget_bp.route('/', methods=['GET'])
@jwt_required()
def get_budgets():
    """Get all budgets"""
    try:
        budgets = Budget.query.all()
        
        # Calculate utilization for each budget
        result = []
        for budget in budgets:
            budget_data = budget.to_dict()
            utilization = calculate_budget_utilization(budget)
            budget_data.update(utilization)
            result.append(budget_data)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@budget_bp.route('/<int:budget_id>', methods=['GET'])
@jwt_required()
def get_budget(budget_id):
    """Get specific budget with details"""
    try:
        budget = Budget.query.get_or_404(budget_id)
        
        budget_data = budget.to_dict()
        utilization = calculate_budget_utilization(budget)
        budget_data.update(utilization)
        
        # Get related transactions
        transactions = Transaction.query.filter(
            and_(
                Transaction.cost_center_id == budget.cost_center_id,
                Transaction.transaction_date >= budget.period_start,
                Transaction.transaction_date <= budget.period_end
            )
        ).all()
        
        budget_data['transactions'] = [t.to_dict() for t in transactions]
        
        return jsonify(budget_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@budget_bp.route('/', methods=['POST'])
@jwt_required()
def create_budget():
    """Create a new budget"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['cost_center_id', 'amount', 'period_start', 'period_end']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if cost center exists
        cost_center = CostCenter.query.get(data['cost_center_id'])
        if not cost_center:
            return jsonify({'error': 'Cost center not found'}), 404
        
        # Parse dates
        period_start = datetime.strptime(data['period_start'], '%Y-%m-%d').date()
        period_end = datetime.strptime(data['period_end'], '%Y-%m-%d').date()
        
        # Create budget
        new_budget = Budget(
            cost_center_id=data['cost_center_id'],
            amount=data['amount'],
            period_start=period_start,
            period_end=period_end
        )
        
        db.session.add(new_budget)
        db.session.commit()
        
        budget_data = new_budget.to_dict()
        budget_data.update(calculate_budget_utilization(new_budget))
        
        return jsonify({
            'message': 'Budget created successfully',
            'budget': budget_data
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@budget_bp.route('/<int:budget_id>', methods=['PUT'])
@jwt_required()
def update_budget(budget_id):
    """Update a budget"""
    try:
        budget = Budget.query.get_or_404(budget_id)
        data = request.get_json()
        
        # Update fields if provided
        if 'amount' in data:
            budget.amount = data['amount']
        if 'period_start' in data:
            budget.period_start = datetime.strptime(data['period_start'], '%Y-%m-%d').date()
        if 'period_end' in data:
            budget.period_end = datetime.strptime(data['period_end'], '%Y-%m-%d').date()
        
        budget.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        budget_data = budget.to_dict()
        budget_data.update(calculate_budget_utilization(budget))
        
        return jsonify({
            'message': 'Budget updated successfully',
            'budget': budget_data
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@budget_bp.route('/<int:budget_id>', methods=['DELETE'])
@jwt_required()
def delete_budget(budget_id):
    """Delete a budget"""
    try:
        budget = Budget.query.get_or_404(budget_id)
        
        db.session.delete(budget)
        db.session.commit()
        
        return jsonify({'message': 'Budget deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@budget_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_budget_summary():
    """Get budget summary for dashboard"""
    try:
        # Get all budgets
        budgets = Budget.query.all()
        
        total_budget = sum(b.amount for b in budgets)
        
        # Calculate total spent across all budgets
        total_spent = 0
        over_budget_count = 0
        
        for budget in budgets:
            utilization = calculate_budget_utilization(budget)
            total_spent += utilization['actual_spent']
            if utilization['is_over_budget']:
                over_budget_count += 1
        
        overall_utilization = (total_spent / total_budget * 100) if total_budget > 0 else 0
        
        return jsonify({
            'total_budget': total_budget,
            'total_spent': total_spent,
            'overall_utilization_percentage': round(overall_utilization, 2),
            'remaining_balance': total_budget - total_spent,
            'budget_count': len(budgets),
            'over_budget_count': over_budget_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500