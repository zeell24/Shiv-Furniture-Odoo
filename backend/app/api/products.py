# backend/app/api/products.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.database.connection import get_db
from app.database.models import product_to_dict, oid
from datetime import datetime

products_bp = Blueprint('products', __name__)


@products_bp.route('/', methods=['GET'])
@jwt_required()
def get_products():
    try:
        db = get_db()
        cursor = db.products.find({}).sort('name', 1)
        return jsonify([product_to_dict(d) for d in cursor]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@products_bp.route('/<id>', methods=['GET'])
@jwt_required()
def get_product(id):
    try:
        db = get_db()
        doc = db.products.find_one({'_id': oid(id)})
        if not doc:
            return jsonify({'error': 'Product not found'}), 404
        return jsonify(product_to_dict(doc)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@products_bp.route('/', methods=['POST'])
@jwt_required()
def create_product():
    try:
        data = request.get_json()
        if not data.get('name'):
            return jsonify({'error': 'Product name is required'}), 400

        db = get_db()
        if data.get('sku') and db.products.find_one({'sku': data['sku']}):
            return jsonify({'error': 'Product SKU already exists'}), 400

        doc = {
            'name': data['name'],
            'sku': data.get('sku'),
            'category': data.get('category'),
            'price': float(data.get('price', 0)),
            'description': data.get('description', ''),
            'created_at': datetime.utcnow()
        }
        r = db.products.insert_one(doc)
        doc['_id'] = r.inserted_id
        return jsonify({
            'message': 'Product created successfully',
            'product': product_to_dict(doc)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@products_bp.route('/<id>', methods=['PUT'])
@jwt_required()
def update_product(id):
    try:
        db = get_db()
        doc = db.products.find_one({'_id': oid(id)})
        if not doc:
            return jsonify({'error': 'Product not found'}), 404

        data = request.get_json()
        updates = {}
        if 'name' in data:
            updates['name'] = data['name']
        if 'sku' in data:
            if data['sku'] != doc.get('sku') and db.products.find_one({'sku': data['sku']}):
                return jsonify({'error': 'Product SKU already exists'}), 400
            updates['sku'] = data['sku']
        if 'category' in data:
            updates['category'] = data['category']
        if 'price' in data:
            updates['price'] = data['price']
        if 'description' in data:
            updates['description'] = data['description']
        if updates:
            db.products.update_one({'_id': oid(id)}, {'$set': updates})
        doc = db.products.find_one({'_id': oid(id)})
        return jsonify({
            'message': 'Product updated successfully',
            'product': product_to_dict(doc)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@products_bp.route('/<id>', methods=['DELETE'])
@jwt_required()
def delete_product(id):
    try:
        db = get_db()
        doc = db.products.find_one({'_id': oid(id)})
        if not doc:
            return jsonify({'error': 'Product not found'}), 404
        pid = doc['_id']
        if db.transactions.count_documents({'product_id': pid}) > 0:
            return jsonify({'error': 'Cannot delete product that has transactions'}), 400
        db.products.delete_one({'_id': oid(id)})
        return jsonify({'message': 'Product deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
