# backend/app/api/cost_centers.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.database.connection import db
from app.database.models import CostCenter

cost_centers_bp = Blueprint('cost_centers', __name__)

@cost_centers_bp.route('/', methods=['GET'])
@jwt_required()
def get_cost_centers():
    """Get all cost centers"""
    try:
        cost_centers = CostCenter.query.all()
        return jsonify([cc.to_dict() for cc in cost_centers]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cost_centers_bp.route('/<int:cost_center_id>', methods=['GET'])
@jwt_required()
def get_cost_center(cost_center_id):
    """Get specific cost center"""
    try:
        cost_center = CostCenter.query.get_or_404(cost_center_id)
        return jsonify(cost_center.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cost_centers_bp.route('/', methods=['POST'])
@jwt_required()
def create_cost_center():
    """Create a new cost center"""
    try:
        data = request.get_json()
        
        if not data.get('name') or not data.get('code'):
            return jsonify({'error': 'Name and code are required'}), 400
        
        # Check if code already exists
        existing = CostCenter.query.filter_by(code=data['code']).first()
        if existing:
            return jsonify({'error': 'Cost center code already exists'}), 400
        
        new_cost_center = CostCenter(
            name=data['name'],
            code=data['code'],
            description=data.get('description', '')
        )
        
        db.session.add(new_cost_center)
        db.session.commit()
        
        return jsonify({
            'message': 'Cost center created successfully',
            'cost_center': new_cost_center.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@cost_centers_bp.route('/<int:cost_center_id>', methods=['PUT'])
@jwt_required()
def update_cost_center(cost_center_id):
    """Update a cost center"""
    try:
        cost_center = CostCenter.query.get_or_404(cost_center_id)
        data = request.get_json()
        
        if 'name' in data:
            cost_center.name = data['name']
        if 'code' in data:
            # Check if new code conflicts with others
            if data['code'] != cost_center.code:
                existing = CostCenter.query.filter_by(code=data['code']).first()
                if existing:
                    return jsonify({'error': 'Cost center code already exists'}), 400
                cost_center.code = data['code']
        if 'description' in data:
            cost_center.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Cost center updated successfully',
            'cost_center': cost_center.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@cost_centers_bp.route('/<int:cost_center_id>', methods=['DELETE'])
@jwt_required()
def delete_cost_center(cost_center_id):
    """Delete a cost center"""
    try:
        cost_center = CostCenter.query.get_or_404(cost_center_id)
        
        # Check if cost center is being used
        if cost_center.budgets or cost_center.transactions:
            return jsonify({
                'error': 'Cannot delete cost center that has budgets or transactions'
            }), 400
        
        db.session.delete(cost_center)
        db.session.commit()
        
        return jsonify({'message': 'Cost center deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500