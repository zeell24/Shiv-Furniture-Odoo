# backend/app/main.py - UPDATED WITH ALL IMPORTS
import sys
import os


# ADD THIS: Fix Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# In create_app() function, inside with app.app_context():
try:
    from app.api.auth import auth_bp
    from app.api.budget import budget_bp
    from app.api.cost_centers import cost_centers_bp
    from app.api.transactions import transactions_bp
    from app.api.products import products_bp
    from app.api.invoices import invoices_bp      # ADD THIS
    from app.api.payments import payments_bp      # ADD THIS
    from app.api.reports import reports_bp        # ADD THIS
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(budget_bp, url_prefix='/api/budgets')
    app.register_blueprint(cost_centers_bp, url_prefix='/api/cost-centers')
    app.register_blueprint(transactions_bp, url_prefix='/api/transactions')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(invoices_bp, url_prefix='/api/invoices')      # ADD THIS
    app.register_blueprint(payments_bp, url_prefix='/api/payments')      # ADD THIS
    app.register_blueprint(reports_bp, url_prefix='/api/reports')        # ADD THIS
    
    print("✅ All blueprints registered")
    
except ImportError as e:
    print(f"⚠️  Blueprint import warning: {e}")

# Load environment variables
load_dotenv()

# Initialize SQLAlchemy here (BEFORE importing blueprints)
db = SQLAlchemy()

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
    
    # Initialize extensions
    CORS(app)
    JWTManager(app)
    db.init_app(app)
    
    # Import models FIRST (important!)
    try:
        from app.database import models  # This creates the tables
        print("✅ Models imported")
    except ImportError as e:
        print(f"⚠️  Model import warning: {e}")
    
    # Now import and register blueprints - IMPORTANT: Do it INSIDE app context
    with app.app_context():
        try:
            from app.api.auth import auth_bp
            from app.api.budget import budget_bp
            from app.api.cost_centers import cost_centers_bp
            from app.api.transactions import transactions_bp
            from app.api.products import products_bp
            
            app.register_blueprint(auth_bp, url_prefix='/api/auth')
            app.register_blueprint(budget_bp, url_prefix='/api/budgets')
            app.register_blueprint(cost_centers_bp, url_prefix='/api/cost-centers')
            app.register_blueprint(transactions_bp, url_prefix='/api/transactions')
            app.register_blueprint(products_bp, url_prefix='/api/products')
            
            print("✅ All blueprints registered")
            
        except ImportError as e:
            print(f"⚠️  Blueprint import warning: {e}")
            # Create simple test blueprint if imports fail
            from flask import jsonify
            @app.route('/api/test')
            def test():
                return jsonify({'message': 'API is working (some modules may not be loaded)'})
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables created")
    
    # Add a simple test route
    @app.route('/')
    def home():
        return {
            'message': 'Shiv Furniture Budget API',
            'status': 'Running',
            'endpoints': {
                'test': '/api/auth/test',
                'products': '/api/products/',
                'transactions': '/api/transactions/'
            }
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("=" * 50)
    print("🚀 Shiv Furniture Budget API Starting...")
    print("📡 Server: http://localhost:5000")
    print("🔗 Test: http://localhost:5000/")
    print("=" * 50)
    app.run(debug=True, port=5000)