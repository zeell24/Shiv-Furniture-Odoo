# backend/app/api/reports.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database.connection import db
from app.database.models import Budget, Transaction, Invoice, Payment, CostCenter
from datetime import datetime, timedelta
from sqlalchemy import func, extract

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/budget-vs-actual', methods=['GET'])
@jwt_required()
def budget_vs_actual_report():
    """Budget vs Actual report"""
    try:
        # Get date range from query params
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Get all budgets
        budgets = Budget.query.all()
        
        report_data = []
        total_budget = 0
        total_actual = 0
        
        for budget in budgets:
            # Calculate actual spending for this budget period
            transactions = Transaction.query.filter(
                Transaction.cost_center_id == budget.cost_center_id,
                Transaction.transaction_date >= budget.period_start,
                Transaction.transaction_date <= budget.period_end
            ).all()
            
            actual_spent = sum(t.amount for t in transactions)
            utilization = (actual_spent / budget.amount * 100) if budget.amount > 0 else 0
            
            report_data.append({
                'budget_id': budget.id,
                'cost_center_id': budget.cost_center_id,
                'cost_center_name': budget.cost_center.name if budget.cost_center else None,
                'budget_amount': budget.amount,
                'actual_spent': actual_spent,
                'variance': budget.amount - actual_spent,
                'utilization_percentage': round(utilization, 2),
                'period_start': budget.period_start.isoformat(),
                'period_end': budget.period_end.isoformat()
            })
            
            total_budget += budget.amount
            total_actual += actual_spent
        
        total_variance = total_budget - total_actual
        total_utilization = (total_actual / total_budget * 100) if total_budget > 0 else 0
        
        return jsonify({
            'summary': {
                'total_budget': total_budget,
                'total_actual': total_actual,
                'total_variance': total_variance,
                'overall_utilization': round(total_utilization, 2)
            },
            'details': report_data,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/financial-summary', methods=['GET'])
@jwt_required()
def financial_summary():
    """Financial summary report"""
    try:
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get date range (default: last 30 days)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        # Calculate totals
        total_sales = db.session.query(func.sum(Transaction.amount))\
            .filter(Transaction.type == 'sale')\
            .filter(Transaction.transaction_date >= start_date)\
            .filter(Transaction.transaction_date <= end_date)\
            .scalar() or 0
        
        total_purchases = db.session.query(func.sum(Transaction.amount))\
            .filter(Transaction.type == 'purchase')\
            .filter(Transaction.transaction_date >= start_date)\
            .filter(Transaction.transaction_date <= end_date)\
            .scalar() or 0
        
        total_invoices = db.session.query(func.sum(Invoice.amount))\
            .filter(Invoice.created_at >= start_date)\
            .filter(Invoice.created_at <= end_date)\
            .scalar() or 0
        
        total_payments = db.session.query(func.sum(Payment.amount))\
            .filter(Payment.payment_date >= start_date)\
            .filter(Payment.payment_date <= end_date)\
            .scalar() or 0
        
        # Counts
        invoice_count = Invoice.query.filter(
            Invoice.created_at >= start_date,
            Invoice.created_at <= end_date
        ).count()
        
        paid_invoices = Invoice.query.filter(
            Invoice.status == 'paid',
            Invoice.created_at >= start_date,
            Invoice.created_at <= end_date
        ).count()
        
        payment_count = Payment.query.filter(
            Payment.payment_date >= start_date,
            Payment.payment_date <= end_date
        ).count()
        
        return jsonify({
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'summary': {
                'total_sales': total_sales,
                'total_purchases': total_purchases,
                'gross_profit': total_sales - total_purchases,
                'total_invoices': total_invoices,
                'total_payments': total_payments,
                'outstanding_balance': total_invoices - total_payments
            },
            'counts': {
                'invoices_issued': invoice_count,
                'invoices_paid': paid_invoices,
                'payments_received': payment_count,
                'payment_rate': round((paid_invoices / invoice_count * 100) if invoice_count > 0 else 0, 2)
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/cost-center-performance', methods=['GET'])
@jwt_required()
def cost_center_performance():
    """Cost center performance report"""
    try:
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        cost_centers = CostCenter.query.all()
        
        performance_data = []
        
        for cc in cost_centers:
            # Get budget for this cost center
            budget = Budget.query.filter_by(cost_center_id=cc.id).first()
            
            # Get transactions
            transactions = Transaction.query.filter_by(cost_center_id=cc.id).all()
            
            total_spent = sum(t.amount for t in transactions)
            
            if budget:
                utilization = (total_spent / budget.amount * 100) if budget.amount > 0 else 0
                remaining = budget.amount - total_spent
            else:
                utilization = 0
                remaining = 0
            
            # Count transactions by type
            purchase_count = sum(1 for t in transactions if t.type == 'purchase')
            sale_count = sum(1 for t in transactions if t.type == 'sale')
            
            performance_data.append({
                'cost_center_id': cc.id,
                'cost_center_name': cc.name,
                'cost_center_code': cc.code,
                'total_transactions': len(transactions),
                'purchase_count': purchase_count,
                'sale_count': sale_count,
                'total_spent': total_spent,
                'budget_amount': budget.amount if budget else 0,
                'utilization_percentage': round(utilization, 2),
                'remaining_budget': remaining,
                'is_over_budget': total_spent > (budget.amount if budget else 0)
            })
        
        return jsonify({
            'cost_centers': performance_data,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/dashboard-stats', methods=['GET'])
@jwt_required()
def dashboard_stats():
    """Dashboard statistics"""
    try:
        # Quick stats for dashboard
        total_budgets = Budget.query.count()
        total_transactions = Transaction.query.count()
        total_invoices = Invoice.query.count()
        total_payments = Payment.query.count()
        
        # Today's stats
        today = datetime.now().date()
        today_transactions = Transaction.query.filter(
            Transaction.transaction_date == today
        ).count()
        
        today_sales = db.session.query(func.sum(Transaction.amount))\
            .filter(Transaction.type == 'sale')\
            .filter(Transaction.transaction_date == today)\
            .scalar() or 0
        
        # Recent unpaid invoices
        recent_invoices = Invoice.query.filter(
            Invoice.status.in_(['unpaid', 'partial'])
        ).order_by(Invoice.due_date.asc()).limit(5).all()
        
        # Budget alerts (over 90% utilization)
        budgets = Budget.query.all()
        alert_budgets = []
        
        for budget in budgets:
            transactions = Transaction.query.filter(
                Transaction.cost_center_id == budget.cost_center_id,
                Transaction.transaction_date >= budget.period_start,
                Transaction.transaction_date <= budget.period_end
            ).all()
            
            actual_spent = sum(t.amount for t in transactions)
            utilization = (actual_spent / budget.amount * 100) if budget.amount > 0 else 0
            
            if utilization >= 90:
                alert_budgets.append({
                    'budget_id': budget.id,
                    'cost_center': budget.cost_center.name if budget.cost_center else None,
                    'budget_amount': budget.amount,
                    'actual_spent': actual_spent,
                    'utilization': round(utilization, 2),
                    'remaining': budget.amount - actual_spent
                })
        
        return jsonify({
            'summary': {
                'total_budgets': total_budgets,
                'total_transactions': total_transactions,
                'total_invoices': total_invoices,
                'total_payments': total_payments,
                'today_transactions': today_transactions,
                'today_sales': today_sales
            },
            'alerts': {
                'budget_alerts': alert_budgets,
                'alert_count': len(alert_budgets)
            },
            'recent_unpaid_invoices': [inv.to_dict() for inv in recent_invoices],
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500