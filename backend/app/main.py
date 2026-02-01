# backend/app/main.py - Flask app with MongoDB (online)
"""
App factory: MongoDB is initialized in create_app via init_mongodb(app).
Set MONGO_URI and MONGO_DB_NAME in .env (e.g. MongoDB Atlas connection string).
"""
import sys
import os

_backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_root not in sys.path:
    sys.path.insert(0, _backend_root)

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Load .env from current dir and from project root (parent of backend) so MONGO_URI is found
load_dotenv()
_project_root = os.path.abspath(os.path.join(_backend_root, '..'))
_env_path = os.path.join(_project_root, '.env')
if os.path.isfile(_env_path):
    load_dotenv(_env_path)

from app.database.connection import init_mongodb


def create_app():
    """Application factory pattern - uses MongoDB (online)."""
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-me')
    app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    app.config['MONGO_DB_NAME'] = os.getenv('MONGO_DB_NAME', 'shiv_furniture_db')

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    jwt = JWTManager(app)

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"error": "Invalid or expired token. Please sign in again."}), 401

    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({"error": "Missing or invalid authorization header."}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token has expired. Please sign in again."}), 401

    init_mongodb(app)
    print("[OK] MongoDB connected")

    try:
        from app.api.auth import auth_bp
        from app.api.budget import budget_bp
        from app.api.cost_centers import cost_centers_bp
        from app.api.transactions import transactions_bp
        from app.api.products import products_bp
        from app.api.invoices import invoices_bp
        from app.api.payments import payments_bp
        from app.api.reports import reports_bp

        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(budget_bp, url_prefix='/api/budgets')
        app.register_blueprint(cost_centers_bp, url_prefix='/api/cost-centers')
        app.register_blueprint(transactions_bp, url_prefix='/api/transactions')
        app.register_blueprint(products_bp, url_prefix='/api/products')
        app.register_blueprint(invoices_bp, url_prefix='/api/invoices')
        app.register_blueprint(payments_bp, url_prefix='/api/payments')
        app.register_blueprint(reports_bp, url_prefix='/api/reports')
        print("[OK] All blueprints registered")
    except ImportError as e:
        print("[WARN] Blueprint import warning:", e)

    @app.route('/')
    def home():
        return jsonify({
            'message': 'Shiv Furniture Budget API',
            'status': 'Running',
            'database': 'MongoDB',
            'endpoints': {
                'auth': '/api/auth/',
                'products': '/api/products/',
                'transactions': '/api/transactions/',
                'budgets': '/api/budgets/',
                'invoices': '/api/invoices/',
                'payments': '/api/payments/',
                'reports': '/api/reports/'
            }
        })

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'healthy', 'service': 'Shiv Furniture Budget API', 'database': 'MongoDB'})

    return app


if __name__ == '__main__':
    app = create_app()
    print("=" * 50)
    print("Shiv Furniture Budget API (MongoDB)")
    print("Server: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)
