from flask import current_app
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging

logger = logging.getLogger(__name__)

# Global MongoDB connection
mongo_client = None
db = None

def init_mongodb(app):
    """Initialize MongoDB connection"""
    global mongo_client, db
    
    try:
        # Create MongoDB client
        mongo_client = MongoClient(
            app.config['MONGO_URI'],
            serverSelectionTimeoutMS=5000,
            maxPoolSize=50
        )
        
        # Test connection
        mongo_client.admin.command('ping')
        
        # Get database
        db = mongo_client[app.config['MONGO_DB_NAME']]
        
        # Store in app config for easy access
        app.config['MONGO_CLIENT'] = mongo_client
        app.config['MONGO_DB'] = db
        
        logger.info(f"Connected to MongoDB: {app.config['MONGO_DB_NAME']}")
        
        # Create indexes (optional, can be moved to init_db.py)
        create_indexes(db)
        
        return db
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

def create_indexes(db):
    """Create necessary indexes for collections"""
    
    # Users collection
    db.users.create_index('email', unique=True)
    db.users.create_index('username', unique=True)
    
    # Products collection
    db.products.create_index('sku', unique=True)
    db.products.create_index('name')
    
    # Contacts collection
    db.contacts.create_index('email', unique=True)
    db.contacts.create_index('contact_type')
    
    # Analytical Accounts (Cost Centers)
    db.analytical_accounts.create_index('code', unique=True)
    db.analytical_accounts.create_index('parent_code')
    
    # Budgets collection
    db.budgets.create_index([('analytical_account_id', 1), ('start_date', 1), ('end_date', 1)])
    db.budgets.create_index('status')
    
    # Transactions collection
    db.transactions.create_index('transaction_date')
    db.transactions.create_index('analytical_account_id')
    db.transactions.create_index([('type', 1), ('status', 1)])
    
    # Invoices collection
    db.invoices.create_index('invoice_number', unique=True)
    db.invoices.create_index('contact_id')
    db.invoices.create_index('due_date')
    
    # Payments collection
    db.payments.create_index('payment_date')
    db.payments.create_index('invoice_id')
    db.payments.create_index('payment_method')
    
    logger.info("Database indexes created successfully")

def get_db():
    """Get database instance"""
    return db

def get_mongo_client():
    """Get MongoDB client instance"""
    return mongo_client