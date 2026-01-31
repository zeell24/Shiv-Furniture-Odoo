from flask import Flask, jsonify
from flask_cors import CORS
from .config import Config
from .database.connection import init_mongodb
import logging

def create_app():
    """Factory function to create Flask app"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize MongoDB
    init_mongodb(app)
    
    # Register blueprints/API routes (to be added later)
    # from .api import budget_bp, cost_centers_bp, transactions_bp
    # app.register_blueprint(budget_bp, url_prefix='/api/budgets')
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'Shiv Furniture Budget System',
            'database': 'connected' if app.config['MONGO_CLIENT'] else 'disconnected'
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

# For running directly with python main.py
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)