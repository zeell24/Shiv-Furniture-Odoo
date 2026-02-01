# backend/app/api/reports.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database.connection import get_db
from app.database.models import transaction_to_dict, budget_to_dict, invoice_to_dict, oid
from datetime import datetime, timedelta
from collections import defaultdict

reports_bp = Blueprint('reports', __name__)


def _doc_date(doc, key):
    v = doc.get(key)
    if v is None:
        return None
    if hasattr(v, 'date'):
        return v.date() if hasattr(v, 'date') else v
    if isinstance(v, str):
        return datetime.strptime(v[:10], '%Y-%m-%d').date()
    return v


@reports_bp.route('/chart-data', methods=['GET'])
@jwt_required()
def chart_data():
    try:
        db = get_db()
        transactions = list(db.transactions.find({}).sort('transaction_date', 1))
        if not transactions:
            return jsonify({
                'labels': [], 'datasets': [], 'has_data': False,
                'message': 'No transaction data yet. Add transactions to see the chart.'
            }), 200
        by_month = defaultdict(lambda: {'purchase': 0, 'sale': 0, 'total': 0})
        months_seen = set()
        for t in transactions:
            dt = _doc_date(t, 'transaction_date')
            month_key = dt.strftime('%Y-%m') if dt else 'Unknown'
            months_seen.add(month_key)
            by_month[month_key][t.get('type', '')] += t.get('amount', 0)
            by_month[month_key]['total'] += t.get('amount', 0)
        labels = sorted(months_seen)
        return jsonify({
            'labels': labels,
            'datasets': [
                {'label': 'Purchases', 'data': [by_month[m]['purchase'] for m in labels], 'backgroundColor': '#ef4444'},
                {'label': 'Sales', 'data': [by_month[m]['sale'] for m in labels], 'backgroundColor': '#22c55e'},
                {'label': 'Total', 'data': [by_month[m]['total'] for m in labels], 'backgroundColor': '#3b82f6'}
            ],
            'has_data': True,
            'transactions': [transaction_to_dict(t) for t in transactions]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reports_bp.route('/budget-vs-actual', methods=['GET'])
@jwt_required()
def budget_vs_actual_report():
    try:
        db = get_db()
        budgets = list(db.budgets.find({}))
        report_data = []
        total_budget = 0
        total_actual = 0
        for budget in budgets:
            cc_id = budget.get('cost_center_id')
            ps = _doc_date(budget, 'period_start')
            pe = _doc_date(budget, 'period_end')
            amt = budget.get('amount', 0)
            txns = list(db.transactions.find({
                'cost_center_id': cc_id,
                'transaction_date': {'$gte': ps, '$lte': pe}
            }))
            actual_spent = sum(t.get('amount', 0) for t in txns)
            utilization = (actual_spent / amt * 100) if amt > 0 else 0
            cc = db.cost_centers.find_one({'_id': cc_id})
            report_data.append({
                'budget_id': str(budget['_id']),
                'cost_center_id': str(cc_id),
                'cost_center_name': cc.get('name') if cc else None,
                'budget_amount': amt,
                'actual_spent': actual_spent,
                'variance': amt - actual_spent,
                'utilization_percentage': round(utilization, 2),
                'period_start': ps.isoformat() if ps else None,
                'period_end': pe.isoformat() if pe else None
            })
            total_budget += amt
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
    try:
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        db = get_db()
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())

        pipeline_txn = [
            {'$match': {'transaction_date': {'$gte': start_date, '$lte': end_date}}},
            {'$group': {'_id': '$type', 'total': {'$sum': '$amount'}}}
        ]
        agg = list(db.transactions.aggregate(pipeline_txn))
        by_type = {x['_id']: x['total'] for x in agg}
        total_sales = by_type.get('sale', 0)
        total_purchases = by_type.get('purchase', 0)

        total_invoices = db.invoices.aggregate([
            {'$match': {'created_at': {'$gte': start_dt, '$lte': end_dt}}},
            {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
        ])
        total_invoices = next(total_invoices, {}).get('total', 0)

        total_payments = db.payments.aggregate([
            {'$match': {'payment_date': {'$gte': start_dt, '$lte': end_dt}}},
            {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
        ])
        total_payments = next(total_payments, {}).get('total', 0)

        invoice_count = db.invoices.count_documents({'created_at': {'$gte': start_dt, '$lte': end_dt}})
        paid_invoices = db.invoices.count_documents({
            'status': 'paid',
            'created_at': {'$gte': start_dt, '$lte': end_dt}
        })
        payment_count = db.payments.count_documents({'payment_date': {'$gte': start_dt, '$lte': end_dt}})

        return jsonify({
            'period': {'start_date': start_date.isoformat(), 'end_date': end_date.isoformat()},
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
    try:
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        db = get_db()
        cost_centers = list(db.cost_centers.find({}))
        performance_data = []
        for cc in cost_centers:
            cc_id = cc['_id']
            budget = db.budgets.find_one({'cost_center_id': cc_id})
            transactions = list(db.transactions.find({'cost_center_id': cc_id}))
            total_spent = sum(t.get('amount', 0) for t in transactions)
            amt = budget.get('amount', 0) if budget else 0
            utilization = (total_spent / amt * 100) if amt > 0 else 0
            remaining = amt - total_spent
            purchase_count = sum(1 for t in transactions if t.get('type') == 'purchase')
            sale_count = sum(1 for t in transactions if t.get('type') == 'sale')
            performance_data.append({
                'cost_center_id': str(cc_id),
                'cost_center_name': cc.get('name'),
                'cost_center_code': cc.get('code'),
                'total_transactions': len(transactions),
                'purchase_count': purchase_count,
                'sale_count': sale_count,
                'total_spent': total_spent,
                'budget_amount': amt,
                'utilization_percentage': round(utilization, 2),
                'remaining_budget': remaining,
                'is_over_budget': total_spent > amt
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
    try:
        db = get_db()
        total_budgets = db.budgets.count_documents({})
        total_transactions = db.transactions.count_documents({})
        total_invoices = db.invoices.count_documents({})
        total_payments = db.payments.count_documents({})

        today = datetime.now().date()
        today_transactions = db.transactions.count_documents({'transaction_date': today})
        pipeline = [
            {'$match': {'type': 'sale', 'transaction_date': today}},
            {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
        ]
        agg = list(db.transactions.aggregate(pipeline))
        today_sales = agg[0]['total'] if agg else 0

        recent_invoices = list(db.invoices.find(
            {'status': {'$in': ['unpaid', 'partial']}}
        ).sort('due_date', 1).limit(5))
        paid_map = {}
        for inv in recent_invoices:
            paid_map[inv['_id']] = sum(p['amount'] for p in db.payments.find({'invoice_id': inv['_id']}))
        recent_out = []
        for inv in recent_invoices:
            cust = db.users.find_one({'_id': inv.get('customer_id')})
            recent_out.append(invoice_to_dict(inv, customer_email=cust.get('email') if cust else None, paid_amount=paid_map.get(inv['_id'], 0)))

        budgets = list(db.budgets.find({}))
        alert_budgets = []
        for budget in budgets:
            cc_id = budget.get('cost_center_id')
            ps = _doc_date(budget, 'period_start')
            pe = _doc_date(budget, 'period_end')
            txns = list(db.transactions.find({
                'cost_center_id': cc_id,
                'transaction_date': {'$gte': ps, '$lte': pe}
            }))
            actual_spent = sum(t.get('amount', 0) for t in txns)
            amt = budget.get('amount', 0)
            utilization = (actual_spent / amt * 100) if amt > 0 else 0
            if utilization >= 90:
                cc = db.cost_centers.find_one({'_id': cc_id})
                alert_budgets.append({
                    'budget_id': str(budget['_id']),
                    'cost_center': cc.get('name') if cc else None,
                    'budget_amount': amt,
                    'actual_spent': actual_spent,
                    'utilization': round(utilization, 2),
                    'remaining': amt - actual_spent
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
            'alerts': {'budget_alerts': alert_budgets, 'alert_count': len(alert_budgets)},
            'recent_unpaid_invoices': recent_out,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
