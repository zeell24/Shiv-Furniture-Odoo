# backend/app/api/cost_centers.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.database.connection import get_db
from app.database.models import cost_center_to_dict, oid
from datetime import datetime

cost_centers_bp = Blueprint('cost_centers', __name__)


@cost_centers_bp.route('/', methods=['GET'])
@jwt_required()
def get_cost_centers():
    try:
        db = get_db()
        cursor = db.cost_centers.find({}).sort('name', 1)
        return jsonify([cost_center_to_dict(d) for d in cursor]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cost_centers_bp.route('/<id>', methods=['GET'])
@jwt_required()
def get_cost_center(id):
    try:
        db = get_db()
        doc = db.cost_centers.find_one({'_id': oid(id)})
        if not doc:
            return jsonify({'error': 'Cost center not found'}), 404
        return jsonify(cost_center_to_dict(doc)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cost_centers_bp.route('/', methods=['POST'])
@jwt_required()
def create_cost_center():
    try:
        data = request.get_json()
        if not data.get('name') or not data.get('code'):
            return jsonify({'error': 'Name and code are required'}), 400

        db = get_db()
        if db.cost_centers.find_one({'code': data['code']}):
            return jsonify({'error': 'Cost center code already exists'}), 400

        doc = {
            'name': data['name'],
            'code': data['code'],
            'description': data.get('description', ''),
            'created_at': datetime.utcnow()
        }
        r = db.cost_centers.insert_one(doc)
        doc['_id'] = r.inserted_id
        return jsonify({
            'message': 'Cost center created successfully',
            'cost_center': cost_center_to_dict(doc)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cost_centers_bp.route('/<id>', methods=['PUT'])
@jwt_required()
def update_cost_center(id):
    try:
        db = get_db()
        doc = db.cost_centers.find_one({'_id': oid(id)})
        if not doc:
            return jsonify({'error': 'Cost center not found'}), 404

        data = request.get_json()
        updates = {}
        if 'name' in data:
            updates['name'] = data['name']
        if 'code' in data:
            if data['code'] != doc.get('code'):
                if db.cost_centers.find_one({'code': data['code']}):
                    return jsonify({'error': 'Cost center code already exists'}), 400
            updates['code'] = data['code']
        if 'description' in data:
            updates['description'] = data['description']
        if not updates:
            return jsonify({'message': 'No changes', 'cost_center': cost_center_to_dict(doc)}), 200

        db.cost_centers.update_one({'_id': oid(id)}, {'$set': updates})
        doc = db.cost_centers.find_one({'_id': oid(id)})
        return jsonify({
            'message': 'Cost center updated successfully',
            'cost_center': cost_center_to_dict(doc)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cost_centers_bp.route('/<id>', methods=['DELETE'])
@jwt_required()
def delete_cost_center(id):
    try:
        db = get_db()
        doc = db.cost_centers.find_one({'_id': oid(id)})
        if not doc:
            return jsonify({'error': 'Cost center not found'}), 404

        cc_id = doc['_id']
        if db.budgets.count_documents({'cost_center_id': cc_id}) > 0 or \
           db.transactions.count_documents({'cost_center_id': cc_id}) > 0:
            return jsonify({'error': 'Cannot delete cost center that has budgets or transactions'}), 400

        db.cost_centers.delete_one({'_id': oid(id)})
        return jsonify({'message': 'Cost center deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
