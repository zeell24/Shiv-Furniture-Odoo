#!/usr/bin/env python3
"""
Database initialization script for Shiv Furniture Budget System
Creates collections, indexes, and seed data
"""

import sys
import os
from datetime import datetime, date, timedelta
from bson import ObjectId

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connection import init_mongodb
from app.database.models import (
    User, Contact, Product, AnalyticalAccount, 
    AutoAnalyticalModel, Budget, Transaction, Invoice, Payment,
    ContactType, TransactionType, InvoiceStatus, PaymentStatus,
    PaymentMethod, BudgetStatus
)
from app.config import Config
from flask import Flask

def create_app_for_script():
    """Create a minimal Flask app for initialization"""
    app = Flask(__name__)
    app.config.from_object(Config)
    return app

def create_collections(db):
    """Create collections if they don't exist"""
    collections = [
        'users', 'contacts', 'products', 'analytical_accounts',
        'auto_analytical_models', 'budgets', 'transactions',
        'invoices', 'payments'
    ]
    
    existing_collections = db.list_collection_names()
    
    for collection in collections:
        if collection not in existing_collections:
            db.create_collection(collection)
            print(f"Created collection: {collection}")
        else:
            print(f"Collection already exists: {collection}")

def create_indexes(db):
    """Create indexes for collections"""
    indexes = {
        'users': [
            [('email', 1), {'unique': True}],
            [('username', 1), {'unique': True}]
        ],
        'contacts': [
            [('email', 1), {'unique': True, 'sparse': True}],
            [('contact_type', 1)]
        ],
        'products': [
            [('sku', 1), {'unique': True}],
            [('name', 1)]
        ],
        'analytical_accounts': [
            [('code', 1), {'unique': True}],
            [('parent_code', 1)]
        ],
        'budgets': [
            [('analytical_account_id', 1), ('start_date', 1), ('end_date', 1)],
            [('status', 1)]
        ],
        'invoices': [
            [('invoice_number', 1), {'unique': True}],
            [('contact_id', 1)],
            [('due_date', 1)]
        ]
    }
    
    for collection, index_list in indexes.items():
        for index_spec in index_list:
            db[collection].create_index(*index_spec)
    
    print("Indexes created successfully")

def seed_sample_data(db):
    """Seed database with sample data"""
    print("\nSeeding sample data...")
    
    # Clear existing data
    for collection in db.list_collection_names():
        if collection != 'system.indexes':
            db[collection].delete_many({})
    
    # 1. Create Analytical Accounts (Cost Centers)
    cost_centers = [
        {
            'code': 'MKT',
            'name': 'Marketing',
            'description': 'Marketing and promotional activities',
            'level': 1,
            'is_group': False,
            'budget_allowed': True
        },
        {
            'code': 'PROD',
            'name': 'Production',
            'description': 'Furniture manufacturing',
            'level': 1,
            'is_group': False,
            'budget_allowed': True
        },
        {
            'code': 'SALES',
            'name': 'Sales',
            'description': 'Sales and distribution',
            'level': 1,
            'is_group': False,
            'budget_allowed': True
        },
        {
            'code': 'ADMIN',
            'name': 'Administration',
            'description': 'General administration',
            'level': 1,
            'is_group': False,
            'budget_allowed': True
        },
        {
            'code': 'HR',
            'name': 'Human Resources',
            'description': 'HR and employee management',
            'level': 1,
            'is_group': False,
            'budget_allowed': True
        }
    ]
    
    analytical_accounts = []
    for cc in cost_centers:
        result = db.analytical_accounts.insert_one(cc)
        analytical_accounts.append(str(result.inserted_id))
    
    print(f"Created {len(analytical_accounts)} analytical accounts")
    
    # 2. Create Contacts
    contacts = [
        {
            'name': 'John Furniture Mart',
            'email': 'john@furnituremart.com',
            'phone': '+91 9876543210',
            'address': '123 Market Street, Delhi',
            'contact_type': 'customer',
            'tax_id': '27ABCDE1234F1Z5',
            'credit_limit': 500000,
            'current_balance': 150000
        },
        {
            'name': 'Wood Suppliers Ltd',
            'email': 'supply@woodsuppliers.com',
            'phone': '+91 9876543211',
            'address': '456 Industrial Area, Mumbai',
            'contact_type': 'vendor',
            'tax_id': '27XYZWV9876A2B3',
            'credit_limit': 0,
            'current_balance': -75000
        },
        {
            'name': 'Rajesh Kumar',
            'email': 'rajesh@example.com',
            'phone': '+91 9876543212',
            'address': '789 Residential Area, Bangalore',
            'contact_type': 'customer',
            'tax_id': '29PQRSM5678T9U0',
            'credit_limit': 200000,
            'current_balance': 50000
        }
    ]
    
    contact_ids = []
    for contact in contacts:
        result = db.contacts.insert_one(contact)
        contact_ids.append(str(result.inserted_id))
    
    print(f"Created {len(contact_ids)} contacts")
    
    # 3. Create Products
    products = [
        {
            'sku': 'WOOD-001',
            'name': 'Teak Wood Plank',
            'description': 'High quality teak wood, 1 inch thick',
            'category': 'wood',
            'unit_price': 1200,
            'cost_price': 900,
            'current_stock': 100,
            'min_stock': 20,
            'max_stock': 500,
            'unit_of_measure': 'pcs'
        },
        {
            'sku': 'FURN-001',
            'name': 'Office Chair',
            'description': 'Ergonomic office chair with lumbar support',
            'category': 'furniture',
            'unit_price': 4500,
            'cost_price': 3200,
            'current_stock': 50,
            'min_stock': 10,
            'max_stock': 200,
            'unit_of_measure': 'pcs'
        },
        {
            'sku': 'FAB-001',
            'name': 'Cotton Fabric Roll',
            'description': 'Premium cotton fabric for upholstery',
            'category': 'fabric',
            'unit_price': 800,
            'cost_price': 550,
            'current_stock': 30,
            'min_stock': 5,
            'max_stock': 100,
            'unit_of_measure': 'roll'
        }
    ]
    
    product_ids = []
    for product in products:
        result = db.products.insert_one(product)
        product_ids.append(str(result.inserted_id))
    
    print(f"Created {len(product_ids)} products")
    
    # 4. Create Budgets
    today = date.today()
    budgets = [
        {
            'name': 'Q1 Marketing Budget',
            'description': 'First quarter marketing activities',
            'analytical_account_id': ObjectId(analytical_accounts[0]),  # MKT
            'start_date': today.replace(month=1, day=1),
            'end_date': today.replace(month=3, day=31),
            'allocated_amount': 500000,
            'currency': 'INR',
            'status': 'active',
            'actual_amount': 125000,
            'achievement_percentage': 25.0
        },
        {
            'name': 'Annual Production Budget',
            'description': 'Yearly production and manufacturing',
            'analytical_account_id': ObjectId(analytical_accounts[1]),  # PROD
            'start_date': today.replace(month=1, day=1),
            'end_date': today.replace(month=12, day=31),
            'allocated_amount': 2000000,
            'currency': 'INR',
            'status': 'active',
            'actual_amount': 850000,
            'achievement_percentage': 42.5
        }
    ]
    
    budget_ids = []
    for budget in budgets:
        budget['remaining_amount'] = budget['allocated_amount'] - budget['actual_amount']
        result = db.budgets.insert_one(budget)
        budget_ids.append(str(result.inserted_id))
    
    print(f"Created {len(budget_ids)} budgets")
    
    # 5. Create Auto-Analytical Models
    auto_models = [
        {
            'name': 'Wood Products to Production',
            'description': 'Automatically assign wood products to Production cost center',
            'conditions': [
                {
                    'field': 'product_category',
                    'operator': 'equals',
                    'value': 'wood'
                }
            ],
            'analytical_account_id': ObjectId(analytical_accounts[1]),  # PROD
            'priority': 1,
            'is_active': True
        },
        {
            'name': 'Furniture Sales to Sales Dept',
            'description': 'Assign furniture sales to Sales department',
            'conditions': [
                {
                    'field': 'product_category',
                    'operator': 'equals',
                    'value': 'furniture'
                },
                {
                    'field': 'transaction_type',
                    'operator': 'equals',
                    'value': 'sale'
                }
            ],
            'analytical_account_id': ObjectId(analytical_accounts[2]),  # SALES
            'priority': 2,
            'is_active': True
        }
    ]
    
    for model in auto_models:
        db.auto_analytical_models.insert_one(model)
    
    print("Created auto-analytical models")
    
    # 6. Create Sample Transactions
    transactions = [
        {
            'transaction_number': 'TXN-2024-001',
            'transaction_date': today - timedelta(days=10),
            'type': 'purchase',
            'contact_id': ObjectId(contact_ids[1]),  # Wood Suppliers
            'analytical_account_id': ObjectId(analytical_accounts[1]),  # PROD
            'description': 'Purchase of teak wood planks',
            'total_amount': 120000,
            'tax_amount': 21600,  # 18% GST
            'net_amount': 141600,
            'currency': 'INR',
            'status': 'posted',
            'reference_number': 'PO-001',
            'items': [
                {
                    'product_id': ObjectId(product_ids[0]),
                    'product_name': 'Teak Wood Plank',
                    'quantity': 100,
                    'unit_price': 1200,
                    'tax_rate': 18,
                    'total': 141600
                }
            ]
        },
        {
            'transaction_number': 'TXN-2024-002',
            'transaction_date': today - timedelta(days=5),
            'type': 'sale',
            'contact_id': ObjectId(contact_ids[0]),  # John Furniture Mart
            'analytical_account_id': ObjectId(analytical_accounts[2]),  # SALES
            'description': 'Sale of office chairs',
            'total_amount': 225000,
            'tax_amount': 40500,  # 18% GST
            'net_amount': 265500,
            'currency': 'INR',
            'status': 'posted',
            'reference_number': 'SO-001',
            'items': [
                {
                    'product_id': ObjectId(product_ids[1]),
                    'product_name': 'Office Chair',
                    'quantity': 50,
                    'unit_price': 4500,
                    'tax_rate': 18,
                    'total': 265500
                }
            ]
        }
    ]
    
    for transaction in transactions:
        result = db.transactions.insert_one(transaction)
    
    print("Created sample transactions")
    
    # 7. Create Sample Invoices
    invoices = [
        {
            'invoice_number': 'INV-2024-001',
            'invoice_date': today - timedelta(days=5),
            'due_date': today + timedelta(days=25),
            'contact_id': ObjectId(contact_ids[0]),
            'transaction_id': ObjectId(transactions[1]['_id']) if '_id' in transactions[1] else None,
            'analytical_account_id': ObjectId(analytical_accounts[2]),
            'sub_total': 225000,
            'tax_amount': 40500,
            'total_amount': 265500,
            'paid_amount': 100000,
            'status': 'partially_paid',
            'payment_terms': 'Net 30',
            'notes': 'Payment partially received',
            'items': transactions[1]['items']
        }
    ]
    
    for invoice in invoices:
        invoice['due_amount'] = invoice['total_amount'] - invoice['paid_amount']
        db.invoices.insert_one(invoice)
    
    print("Created sample invoices")
    
    # 8. Create Sample Payment
    payments = [
        {
            'payment_number': 'PAY-2024-001',
            'payment_date': today - timedelta(days=2),
            'contact_id': ObjectId(contact_ids[0]),
            'invoice_id': ObjectId(invoices[0]['_id']) if '_id' in invoices[0] else None,
            'amount': 100000,
            'payment_method': 'bank_transfer',
            'status': 'completed',
            'reference_number': 'BTRF-001',
            'notes': 'First installment payment'
        }
    ]
    
    for payment in payments:
        db.payments.insert_one(payment)
    
    print("Created sample payments")
    
    # 9. Create Admin User
    # In production, hash the password properly
    admin_user = {
        'username': 'admin',
        'email': 'admin@shivfurniture.com',
        'password_hash': 'hashed_password_here',  # Use bcrypt in production
        'full_name': 'System Administrator',
        'role': 'admin',
        'last_login': datetime.utcnow()
    }
    
    db.users.insert_one(admin_user)
    print("Created admin user")
    
    print("\n✅ Database initialization completed successfully!")
    print(f"📊 Collections created: {len(db.list_collection_names())}")
    
    # Print summary
    print("\n📋 Database Summary:")
    for collection in db.list_collection_names():
        if collection != 'system.indexes':
            count = db[collection].count_documents({})
            print(f"  - {collection}: {count} documents")

def main():
    """Main initialization function"""
    print("🚀 Initializing Shiv Furniture Budget System Database...")
    
    try:
        # Create app and initialize MongoDB
        app = create_app_for_script()
        db = init_mongodb(app)
        
        # Create collections and indexes
        create_collections(db)
        create_indexes(db)
        
        # Ask for seed data
        seed_option = input("\nDo you want to seed sample data? (y/n): ").strip().lower()
        if seed_option in ['y', 'yes']:
            seed_sample_data(db)
        else:
            print("Skipping seed data.")
        
        print("\n✅ Database setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during database initialization: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()