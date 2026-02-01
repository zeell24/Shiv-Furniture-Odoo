# backend/app/api/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.database.connection import get_db
from app.database.models import user_to_dict, user_check_password, user_set_password, oid
from datetime import timedelta, datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400

        db = get_db()
        if db.users.find_one({'email': data['email']}):
            return jsonify({'error': 'User already exists'}), 400

        doc = {
            'email': data['email'],
            'role': data.get('role', 'customer'),
            'password_hash': user_set_password(data['password']),
            'created_at': datetime.utcnow()
        }
        r = db.users.insert_one(doc)
        doc['_id'] = r.inserted_id
        return jsonify({
            'message': 'User registered successfully',
            'user': {'id': str(r.inserted_id), 'email': doc['email'], 'role': doc['role']}
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400

        db = get_db()
        user = db.users.find_one({'email': data['email']})
        if not user or not user_check_password(user.get('password_hash'), data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401

        identity = {'id': str(user['_id']), 'email': user['email'], 'role': user['role']}
        access_token = create_access_token(identity=identity, expires_delta=timedelta(hours=24))
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': {'id': identity['id'], 'email': user['email'], 'role': user['role']}
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        current_user = get_jwt_identity()
        db = get_db()
        user = db.users.find_one({'_id': oid(current_user['id'])})
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(user_to_dict(user)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({'message': 'Logout successful'}), 200


@auth_bp.route('/demo', methods=['POST'])
def demo_login():
    try:
        db = get_db()
        admin = db.users.find_one({'email': 'admin@shivfurniture.com'})
        if not admin:
            db.users.insert_one({
                'email': 'admin@shivfurniture.com',
                'role': 'admin',
                'password_hash': user_set_password('admin123'),
                'created_at': datetime.utcnow()
            })
            admin = db.users.find_one({'email': 'admin@shivfurniture.com'})
        else:
            db.users.update_one(
                {'_id': admin['_id']},
                {'$set': {'password_hash': user_set_password('admin123')}}
            )
            admin = db.users.find_one({'email': 'admin@shivfurniture.com'})
        if not admin or not user_check_password(admin.get('password_hash'), 'admin123'):
            return jsonify({'error': 'Demo user setup failed'}), 500
        identity = {'id': str(admin['_id']), 'email': admin['email'], 'role': admin['role']}
        token = create_access_token(identity=identity, expires_delta=timedelta(hours=24))
        return jsonify({
            'message': 'Demo login successful',
            'access_token': token,
            'user': {'id': identity['id'], 'email': admin['email'], 'role': admin['role']}
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
