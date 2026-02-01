# backend/app/api/budget.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.database.connection import get_db
from app.database.models import budget_to_dict, transaction_to_dict, master_budget_to_dict, cost_center_to_dict, oid
from datetime import datetime, date

budget_bp = Blueprint('budget', __name__)


def _date_parse(s):
    if isinstance(s, date):
        return s
    if isinstance(s, datetime):
        return s.date()
    return datetime.strptime(s, '%Y-%m-%d').date() if s else None


def _doc_date(doc, key):
    v = doc.get(key)
    if v is None:
        return None
    if hasattr(v, 'date'):
        return v
    if isinstance(v, str):
        return datetime.strptime(v[:10], '%Y-%m-%d').date()
    return v


def calculate_budget_utilization(db, budget_doc):
    cc_id = budget_doc.get('cost_center_id')
    period_start = _doc_date(budget_doc, 'period_start')
    period_end = _doc_date(budget_doc, 'period_end')
    amount = budget_doc.get('amount', 0)
    if not cc_id or not period_start or not period_end:
        return {'budget_amount': amount, 'actual_spent': 0, 'utilization_percentage': 0, 'remaining_balance': amount, 'is_over_budget': False}
    transactions = list(db.transactions.find({
        'cost_center_id': cc_id,
        'transaction_date': {'$gte': period_start, '$lte': period_end}
    }))
    total_spent = sum(t.get('amount', 0) for t in transactions)
    utilization = (total_spent / amount * 100) if amount > 0 else 0
    return {
        'budget_amount': amount,
        'actual_spent': total_spent,
        'utilization_percentage': round(utilization, 2),
        'remaining_balance': amount - total_spent,
        'is_over_budget': total_spent > amount
    }


@budget_bp.route('/master', methods=['GET'])
@jwt_required()
def get_master_budget():
    try:
        db = get_db()
        mb = db.master_budget.find_one({})
        if not mb:
            db.master_budget.insert_one({'amount': 1500000, 'updated_at': datetime.utcnow()})
            mb = db.master_budget.find_one({})
        return jsonify({
            'amount': mb['amount'],
            'updated_at': mb.get('updated_at').isoformat() if mb.get('updated_at') else None
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@budget_bp.route('/master', methods=['PUT'])
@jwt_required()
def update_master_budget():
    try:
        data = request.get_json()
        if 'amount' not in data:
            return jsonify({'error': 'amount is required'}), 400
        amount = float(data['amount'])
        if amount < 0:
            return jsonify({'error': 'amount must be positive'}), 400

        db = get_db()
        mb = db.master_budget.find_one({})
        if not mb:
            db.master_budget.insert_one({'amount': amount, 'updated_at': datetime.utcnow()})
        else:
            db.master_budget.update_one({}, {'$set': {'amount': amount, 'updated_at': datetime.utcnow()}})
        mb = db.master_budget.find_one({})
        return jsonify({'message': 'Master budget updated', 'amount': mb['amount']}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@budget_bp.route('/', methods=['GET'])
@jwt_required()
def get_budgets():
    try:
        db = get_db()
        budgets = list(db.budgets.find({}))
        result = []
        for b in budgets:
            cc = db.cost_centers.find_one({'_id': b.get('cost_center_id')})
            name = cc.get('name') if cc else None
            d = budget_to_dict(b, cost_center_name=name)
            d.update(calculate_budget_utilization(db, b))
            result.append(d)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@budget_bp.route('/<id>', methods=['GET'])
@jwt_required()
def get_budget(id):
    try:
        db = get_db()
        budget = db.budgets.find_one({'_id': oid(id)})
        if not budget:
            return jsonify({'error': 'Budget not found'}), 404
        cc = db.cost_centers.find_one({'_id': budget.get('cost_center_id')})
        name = cc.get('name') if cc else None
        d = budget_to_dict(budget, cost_center_name=name)
        d.update(calculate_budget_utilization(db, budget))
        cc_id = budget.get('cost_center_id')
        ps = _doc_date(budget, 'period_start')
        pe = _doc_date(budget, 'period_end')
        txns = list(db.transactions.find({
            'cost_center_id': cc_id,
            'transaction_date': {'$gte': ps, '$lte': pe}
        }))
        d['transactions'] = [transaction_to_dict(t, cost_center_name=name) for t in txns]
        return jsonify(d), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@budget_bp.route('/', methods=['POST'])
@jwt_required()
def create_budget():
    try:
        data = request.get_json()
        required = ['cost_center_id', 'amount', 'period_start', 'period_end']
        for f in required:
            if f not in data:
                return jsonify({'error': f'{f} is required'}), 400

        db = get_db()
        cc_id = oid(data['cost_center_id'])
        if not db.cost_centers.find_one({'_id': cc_id}):
            return jsonify({'error': 'Cost center not found'}), 404

        period_start = _date_parse(data['period_start'])
        period_end = _date_parse(data['period_end'])
        doc = {
            'cost_center_id': cc_id,
            'amount': float(data['amount']),
            'period_start': period_start,
            'period_end': period_end,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        r = db.budgets.insert_one(doc)
        doc['_id'] = r.inserted_id
        cc = db.cost_centers.find_one({'_id': cc_id})
        d = budget_to_dict(doc, cost_center_name=cc.get('name') if cc else None)
        d.update(calculate_budget_utilization(db, doc))
        return jsonify({'message': 'Budget created successfully', 'budget': d}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@budget_bp.route('/<id>', methods=['PUT'])
@jwt_required()
def update_budget(id):
    try:
        db = get_db()
        budget = db.budgets.find_one({'_id': oid(id)})
        if not budget:
            return jsonify({'error': 'Budget not found'}), 404

        data = request.get_json()
        updates = {'updated_at': datetime.utcnow()}
        if 'amount' in data:
            updates['amount'] = data['amount']
        if 'period_start' in data:
            updates['period_start'] = _date_parse(data['period_start'])
        if 'period_end' in data:
            updates['period_end'] = _date_parse(data['period_end'])
        db.budgets.update_one({'_id': oid(id)}, {'$set': updates})
        budget = db.budgets.find_one({'_id': oid(id)})
        cc = db.cost_centers.find_one({'_id': budget.get('cost_center_id')})
        d = budget_to_dict(budget, cost_center_name=cc.get('name') if cc else None)
        d.update(calculate_budget_utilization(db, budget))
        return jsonify({'message': 'Budget updated successfully', 'budget': d}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@budget_bp.route('/<id>', methods=['DELETE'])
@jwt_required()
def delete_budget(id):
    try:
        db = get_db()
        r = db.budgets.delete_one({'_id': oid(id)})
        if r.deleted_count == 0:
            return jsonify({'error': 'Budget not found'}), 404
        return jsonify({'message': 'Budget deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@budget_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_budget_summary():
    try:
        db = get_db()
        budgets = list(db.budgets.find({}))
        total_budget = sum(b.get('amount', 0) for b in budgets)
        total_spent = 0
        over_budget_count = 0
        for b in budgets:
            u = calculate_budget_utilization(db, b)
            total_spent += u['actual_spent']
            if u['is_over_budget']:
                over_budget_count += 1
        overall = (total_spent / total_budget * 100) if total_budget > 0 else 0
        return jsonify({
            'total_budget': total_budget,
            'total_spent': total_spent,
            'overall_utilization_percentage': round(overall, 2),
            'remaining_balance': total_budget - total_spent,
            'budget_count': len(budgets),
            'over_budget_count': over_budget_count
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
