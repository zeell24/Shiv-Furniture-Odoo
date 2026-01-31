# backend/app/api/products.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.database.connection import db
from app.database.models import Product

products_bp = Blueprint('products', __name__)

@products_bp.route('/', methods=['GET'])
@jwt_required()
def get_products():
    """Get all products"""
    try:
        products = Product.query.all()
        return jsonify([p.to_dict() for p in products]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    """Get specific product"""
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify(product.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/', methods=['POST'])
@jwt_required()
def create_product():
    """Create a new product"""
    try:
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'error': 'Product name is required'}), 400
        
        # Check if SKU already exists (if provided)
        if data.get('sku'):
            existing = Product.query.filter_by(sku=data['sku']).first()
            if existing:
                return jsonify({'error': 'Product SKU already exists'}), 400
        
        new_product = Product(
            name=data['name'],
            sku=data.get('sku'),
            category=data.get('category'),
            price=data.get('price', 0.0),
            description=data.get('description', '')
        )
        
        db.session.add(new_product)
        db.session.commit()
        
        return jsonify({
            'message': 'Product created successfully',
            'product': new_product.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """Update a product"""
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        if 'name' in data:
            product.name = data['name']
        if 'sku' in data:
            # Check if new SKU conflicts with others
            if data['sku'] != product.sku:
                existing = Product.query.filter_by(sku=data['sku']).first()
                if existing:
                    return jsonify({'error': 'Product SKU already exists'}), 400
                product.sku = data['sku']
        if 'category' in data:
            product.category = data['category']
        if 'price' in data:
            product.price = data['price']
        if 'description' in data:
            product.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Product updated successfully',
            'product': product.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """Delete a product"""
    try:
        product = Product.query.get_or_404(product_id)
        
        # Check if product is being used in transactions
        if product.transactions:
            return jsonify({
                'error': 'Cannot delete product that has transactions'
            }), 400
        
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({'message': 'Product deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500