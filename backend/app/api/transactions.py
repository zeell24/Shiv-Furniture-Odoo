# backend/app/api/transactions.py
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.database.connection import get_db
from app.database.models import transaction_to_dict, cost_center_to_dict, product_to_dict, oid
from app.utils.json_response import json_response
from datetime import datetime

transactions_bp = Blueprint('transactions', __name__)


def _doc_date(doc, key):
    v = doc.get(key)
    if v is None:
        return None
    if hasattr(v, 'date'):
        return v
    if isinstance(v, str):
        return datetime.strptime(v[:10], '%Y-%m-%d').date()
    return v


@transactions_bp.route('/', methods=['GET'])
@jwt_required()
def get_transactions():
    try:
        db = get_db()
        q = {}
        if request.args.get('type'):
            q['type'] = request.args.get('type')
        if request.args.get('cost_center_id'):
            q['cost_center_id'] = oid(request.args.get('cost_center_id'))
        if request.args.get('start_date'):
            q.setdefault('transaction_date', {})['$gte'] = datetime.strptime(request.args['start_date'], '%Y-%m-%d').date()
        if request.args.get('end_date'):
            q.setdefault('transaction_date', {})['$lte'] = datetime.strptime(request.args['end_date'], '%Y-%m-%d').date()

        cursor = db.transactions.find(q).sort('transaction_date', -1)
        out = []
        for t in cursor:
            cc = db.cost_centers.find_one({'_id': t.get('cost_center_id')})
            pr = db.products.find_one({'_id': t.get('product_id')}) if t.get('product_id') else None
            out.append(transaction_to_dict(t, cost_center_name=cc.get('name') if cc else None, product_name=pr.get('name') if pr else None))
        return json_response(out, 200)
    except Exception as e:
        return json_response({'error': str(e)}, 500)


@transactions_bp.route('/<id>', methods=['GET'])
@jwt_required()
def get_transaction(id):
    try:
        db = get_db()
        t = db.transactions.find_one({'_id': oid(id)})
        if not t:
            return json_response({'error': 'Transaction not found'}, 404)
        cc = db.cost_centers.find_one({'_id': t.get('cost_center_id')})
        pr = db.products.find_one({'_id': t.get('product_id')}) if t.get('product_id') else None
        return json_response(transaction_to_dict(t, cost_center_name=cc.get('name') if cc else None, product_name=pr.get('name') if pr else None), 200)
    except Exception as e:
        return json_response({'error': str(e)}, 500)


@transactions_bp.route('/', methods=['POST'])
@jwt_required()
def create_transaction():
    try:
        data = request.get_json()
        required = ['type', 'amount', 'cost_center_id', 'transaction_date']
        for f in required:
            if f not in data:
                return json_response({'error': f'{f} is required'}, 400)
        if data['type'] not in ('purchase', 'sale'):
            return json_response({'error': "type must be 'purchase' or 'sale'"}, 400)

        db = get_db()
        cc_id = oid(data['cost_center_id'])
        if not db.cost_centers.find_one({'_id': cc_id}):
            return json_response({'error': 'Cost center not found'}, 404)
        product_id = oid(data.get('product_id')) if data.get('product_id') else None
        if product_id and not db.products.find_one({'_id': product_id}):
            return json_response({'error': 'Product not found'}, 404)

        txn_date = datetime.strptime(data['transaction_date'], '%Y-%m-%d').date()
        status = data.get('status', 'paid')
        if status not in ('paid', 'not_paid', 'partially_paid'):
            status = 'paid'

        doc = {
            'type': data['type'],
            'amount': float(data['amount']),
            'status': status,
            'cost_center_id': cc_id,
            'product_id': product_id,
            'quantity': data.get('quantity', 1),
            'description': data.get('description', ''),
            'transaction_date': txn_date,
            'created_at': datetime.utcnow()
        }
        r = db.transactions.insert_one(doc)
        doc['_id'] = r.inserted_id
        cc = db.cost_centers.find_one({'_id': cc_id})
        pr = db.products.find_one({'_id': product_id}) if product_id else None
        payload = {
            'message': 'Transaction created successfully',
            'transaction': transaction_to_dict(doc, cost_center_name=cc.get('name') if cc else None, product_name=pr.get('name') if pr else None)
        }
        return json_response(payload, 201)
    except Exception as e:
        return json_response({'error': str(e)}, 500)


@transactions_bp.route('/<id>', methods=['PUT'])
@jwt_required()
def update_transaction(id):
    try:
        db = get_db()
        t = db.transactions.find_one({'_id': oid(id)})
        if not t:
            return json_response({'error': 'Transaction not found'}, 404)

        data = request.get_json()
        updates = {}
        if 'type' in data:
            if data['type'] not in ('purchase', 'sale'):
                return json_response({'error': "type must be 'purchase' or 'sale'"}, 400)
            updates['type'] = data['type']
        if 'amount' in data:
            updates['amount'] = data['amount']
        if 'cost_center_id' in data:
            cc_id = oid(data['cost_center_id'])
            if not db.cost_centers.find_one({'_id': cc_id}):
                return json_response({'error': 'Cost center not found'}, 404)
            updates['cost_center_id'] = cc_id
        if 'product_id' in data:
            pid = oid(data['product_id']) if data['product_id'] else None
            if pid and not db.products.find_one({'_id': pid}):
                return json_response({'error': 'Product not found'}, 404)
            updates['product_id'] = pid
        if 'quantity' in data:
            updates['quantity'] = data['quantity']
        if 'description' in data:
            updates['description'] = data['description']
        if 'transaction_date' in data:
            updates['transaction_date'] = datetime.strptime(data['transaction_date'], '%Y-%m-%d').date()
        if 'status' in data and data['status'] in ('paid', 'not_paid', 'partially_paid'):
            updates['status'] = data['status']
        if updates:
            db.transactions.update_one({'_id': oid(id)}, {'$set': updates})
        t = db.transactions.find_one({'_id': oid(id)})
        cc = db.cost_centers.find_one({'_id': t.get('cost_center_id')})
        pr = db.products.find_one({'_id': t.get('product_id')}) if t.get('product_id') else None
        payload = {
            'message': 'Transaction updated successfully',
            'transaction': transaction_to_dict(t, cost_center_name=cc.get('name') if cc else None, product_name=pr.get('name') if pr else None)
        }
        return json_response(payload, 200)
    except Exception as e:
        return json_response({'error': str(e)}, 500)


@transactions_bp.route('/<id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(id):
    try:
        db = get_db()
        r = db.transactions.delete_one({'_id': oid(id)})
        if r.deleted_count == 0:
            return json_response({'error': 'Transaction not found'}, 404)
        return json_response({'message': 'Transaction deleted successfully'}, 200)
    except Exception as e:
        return json_response({'error': str(e)}, 500)


@transactions_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_transaction_summary():
    try:
        db = get_db()
        pipeline = [
            {'$group': {'_id': None, 'total': {'$sum': '$amount'}, 'purchase': {'$sum': {'$cond': [{'$eq': ['$type', 'purchase']}, '$amount', 0]}}, 'sale': {'$sum': {'$cond': [{'$eq': ['$type', 'sale']}, '$amount', 0]}}}}
        ]
        agg = list(db.transactions.aggregate(pipeline))
        total_purchase = agg[0]['purchase'] if agg else 0
        total_sales = agg[0]['sale'] if agg else 0
        total_transactions = db.transactions.count_documents({})
        recent = list(db.transactions.find({}).sort('transaction_date', -1).limit(10))
        out = []
        for t in recent:
            cc = db.cost_centers.find_one({'_id': t.get('cost_center_id')})
            pr = db.products.find_one({'_id': t.get('product_id')}) if t.get('product_id') else None
            out.append(transaction_to_dict(t, cost_center_name=cc.get('name') if cc else None, product_name=pr.get('name') if pr else None))
        payload = {
            'total_transactions': total_transactions,
            'total_purchase': total_purchase,
            'total_sales': total_sales,
            'net_flow': total_sales - total_purchase,
            'recent_transactions': out
        }
        return json_response(payload, 200)
    except Exception as e:
        return json_response({'error': str(e)}, 500)
