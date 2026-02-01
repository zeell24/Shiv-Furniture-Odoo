# backend/app/main.py - Flask app with MongoDB (online)
"""
App factory: MongoDB is initialized in create_app via init_mongodb(app).
Set MONGO_URI and MONGO_DB_NAME in .env (e.g. MongoDB Atlas connection string).
"""
import sys
import os
from datetime import date, datetime

_backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_root not in sys.path:
    sys.path.insert(0, _backend_root)

from flask import Flask, jsonify
from flask_cors import CORS

def _sanitize_for_json(obj):
    """Recursively convert date/datetime/ObjectId to JSON-serializable types."""
    if obj is None:
        return None
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize_for_json(v) for v in obj]
    try:
        from bson import ObjectId
        if isinstance(obj, ObjectId):
            return str(obj)
    except ImportError:
        pass
    return obj

try:
    from flask.json.provider import DefaultJSONProvider
    from bson import ObjectId

    class CustomJSONProvider(DefaultJSONProvider):
        """JSON provider: sanitize payload then serialize so date/datetime never reach encoder."""
        def default(self, o):
            if isinstance(o, datetime):
                return o.isoformat()
            if isinstance(o, date):
                return o.isoformat()
            if isinstance(o, ObjectId):
                return str(o)
            return super().default(o)

        def dumps(self, obj, **kwargs):
            return super().dumps(_sanitize_for_json(obj), **kwargs)

    def _install_json_provider(app):
        app.json = CustomJSONProvider(app)
except ImportError:
    import json
    from bson import ObjectId

    class CustomJSONEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, datetime):
                return o.isoformat()
            if isinstance(o, date):
                return o.isoformat()
            if isinstance(o, ObjectId):
                return str(o)
            return super().default(o)

    def _install_json_provider(app):
        app.json_encoder = CustomJSONEncoder
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
    _install_json_provider(app)

    # Force every JSON response through sanitizer so date/datetime never reach the encoder
    _orig_dumps = app.json.dumps
    def _safe_dumps(obj, **kwargs):
        return _orig_dumps(_sanitize_for_json(obj), **kwargs)
    app.json.dumps = _safe_dumps

    # Also patch global jsonify so every jsonify() call (from any blueprint) sanitizes first
    import flask.json as _flask_json
    _orig_jsonify = _flask_json.jsonify
    def _safe_jsonify(*args, **kwargs):
        if not args and not kwargs:
            return _orig_jsonify(*args, **kwargs)
        from flask import current_app
        obj = current_app.json._prepare_response_obj(args, kwargs)
        if obj is not None:
            return _orig_jsonify(_sanitize_for_json(obj))
        return _orig_jsonify(*args, **kwargs)
    _flask_json.jsonify = _safe_jsonify

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
