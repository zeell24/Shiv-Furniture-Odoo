# backend/app/main.py
import sys
import os

# Ensure backend root is on Python path when running as script
_backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_root not in sys.path:
    sys.path.insert(0, _backend_root)

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

load_dotenv()

# Use single db instance from app.database.connection (models import this)
from app.database.connection import db


def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-me')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 
        'sqlite:///shiv_furniture.db'  # Default to SQLite
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions (db is from app.database.connection)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    JWTManager(app)
    db.init_app(app)
    
    # Import models so tables are registered
    with app.app_context():
        from app.database import models  # noqa: F401
        db.create_all()
        print("[OK] Models and tables ready")
    
    # Register all API blueprints
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
    
    # Root and health
    @app.route('/')
    def home():
        return jsonify({
            'message': 'Shiv Furniture Budget API',
            'status': 'Running',
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
        return jsonify({'status': 'healthy', 'service': 'Shiv Furniture Budget API'})
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("=" * 50)
    print("🚀 Shiv Furniture Budget API Starting...")
    print("📡 Server: http://localhost:5000")
    print("🔗 Test: http://localhost:5000/")
    print("=" * 50)
    app.run(debug=True, port=5000)