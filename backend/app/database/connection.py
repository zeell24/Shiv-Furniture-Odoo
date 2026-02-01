# backend/app/database/connection.py - MongoDB (online) for Flask app
from flask import current_app
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging

logger = logging.getLogger(__name__)


def _mask_uri(uri):
    """Mask password in URI for error messages."""
    if not uri or '@' not in uri:
        return uri
    try:
        pre, rest = uri.split('@', 1)
        if '://' in pre:
            scheme, creds = pre.split('://', 1)
            if ':' in creds:
                user, _ = creds.split(':', 1)
                return f"{scheme}://{user}:****@{rest}"
        return uri
    except Exception:
        return uri


def init_mongodb(app):
    """Initialize MongoDB connection using MONGO_URI and MONGO_DB_NAME from config."""
    uri = app.config.get('MONGO_URI', 'mongodb://localhost:27017/')
    db_name = app.config.get('MONGO_DB_NAME', 'shiv_furniture_db')
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000, maxPoolSize=50)
        client.admin.command('ping')
        db = client[db_name]
        app.config['MONGO_CLIENT'] = client
        app.config['MONGO_DB'] = db
        logger.info(f"Connected to MongoDB: {db_name}")
        create_indexes(db)
        return db
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        msg = (
            "Could not connect to MongoDB.\n"
            "  Current MONGO_URI: %s\n"
            "  To use MongoDB Atlas (online):\n"
            "    1. Create a free cluster at https://www.mongodb.com/cloud/atlas\n"
            "    2. Get your connection string and add to .env (in project root or backend/):\n"
            "       MONGO_URI=mongodb+srv://USER:PASSWORD@cluster.mongodb.net/\n"
            "       MONGO_DB_NAME=shiv_furniture_db\n"
            "  To use MongoDB locally: install MongoDB and start the service on port 27017."
        ) % _mask_uri(uri)
        raise RuntimeError(msg) from e


def get_db():
    """Return the MongoDB database instance (use inside request/app context)."""
    return current_app.config['MONGO_DB']


def create_indexes(db):
    """Create indexes for budget API collections."""
    db.users.create_index('email', unique=True)
    db.cost_centers.create_index('code', unique=True)
    db.products.create_index('sku', unique=True)
    db.budgets.create_index([('cost_center_id', 1), ('period_start', 1), ('period_end', 1)])
    db.transactions.create_index('transaction_date')
    db.transactions.create_index('cost_center_id')
    db.transactions.create_index([('type', 1), ('status', 1)])
    db.invoices.create_index('invoice_number', unique=True)
    db.invoices.create_index('customer_id')
    db.invoices.create_index('due_date')
    db.payments.create_index('invoice_id')
    db.payments.create_index('payment_date')
    logger.info("MongoDB indexes created successfully")
