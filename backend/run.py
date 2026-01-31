import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shiv_furniture.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ========== MODELS ==========
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)
    category = db.Column(db.String(50))
    
    def to_dict(self):
        return {
            'id': self.id, 
            'name': self.name, 
            'price': self.price,
            'category': self.category
        }

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20))  # 'purchase' or 'sale'
    amount = db.Column(db.Float)
    description = db.Column(db.String(200))
    date = db.Column(db.String(20))
    
    def to_dict(self):
        return {
            'id': self.id, 
            'type': self.type, 
            'amount': self.amount,
            'description': self.description,
            'date': self.date
        }

class Budget(db.Model):
    __tablename__ = 'budgets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    amount = db.Column(db.Float)
    spent = db.Column(db.Float, default=0)
    
    def to_dict(self):
        remaining = self.amount - self.spent
        percent = (self.spent / self.amount * 100) if self.amount > 0 else 0
        return {
            'id': self.id,
            'name': self.name,
            'amount': self.amount,
            'spent': self.spent,
            'remaining': remaining,
            'percent_used': round(percent, 2)
        }

# ========== ROUTES ==========
@app.route('/')
def home():
    return jsonify({
        'message': 'Shiv Furniture Budget System API',
        'status': 'Running',
        'endpoints': {
            'test': '/api/test',
            'products': '/api/products',
            'transactions': '/api/transactions',
            'budgets': '/api/budgets'
        }
    })

@app.route('/api/test')
def test():
    return jsonify({'status': 'API is working!', 'version': '1.0'})

# PRODUCTS API
@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json()
    product = Product(
        name=data.get('name'),
        price=data.get('price', 0),
        category=data.get('category', '')
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({'message': 'Product created', 'product': product.to_dict()}), 201

# TRANSACTIONS API
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    transactions = Transaction.query.all()
    return jsonify([t.to_dict() for t in transactions])

@app.route('/api/transactions', methods=['POST'])
def create_transaction():
    data = request.get_json()
    transaction = Transaction(
        type=data.get('type', 'sale'),
        amount=data.get('amount', 0),
        description=data.get('description', ''),
        date=data.get('date', '2024-01-01')
    )
    db.session.add(transaction)
    db.session.commit()
    
    # Update budget if it's a purchase
    if transaction.type == 'purchase':
        budgets = Budget.query.all()
        for budget in budgets:
            budget.spent += transaction.amount * 0.1  # Example: 10% of purchase
        db.session.commit()
    
    return jsonify({'message': 'Transaction created', 'transaction': transaction.to_dict()}), 201

# BUDGETS API
@app.route('/api/budgets', methods=['GET'])
def get_budgets():
    budgets = Budget.query.all()
    return jsonify([b.to_dict() for b in budgets])

@app.route('/api/budgets', methods=['POST'])
def create_budget():
    data = request.get_json()
    budget = Budget(
        name=data.get('name'),
        amount=data.get('amount', 0),
        spent=data.get('spent', 0)
    )
    db.session.add(budget)
    db.session.commit()
    return jsonify({'message': 'Budget created', 'budget': budget.to_dict()}), 201

# BUDGET VS ACTUAL REPORT
@app.route('/api/reports/budget-vs-actual')
def budget_vs_actual():
    budgets = Budget.query.all()
    total_budget = sum(b.amount for b in budgets)
    total_spent = sum(b.spent for b in budgets)
    
    return jsonify({
        'total_budget': total_budget,
        'total_spent': total_spent,
        'remaining': total_budget - total_spent,
        'utilization_percent': round((total_spent / total_budget * 100) if total_budget > 0 else 0, 2),
        'budgets': [b.to_dict() for b in budgets]
    })

# Initialize database and add sample data
with app.app_context():
    db.create_all()
    
    # Add sample data if empty
    if Product.query.count() == 0:
        sample_products = [
            Product(name="Wooden Chair", price=2999.99, category="Furniture"),
            Product(name="Office Desk", price=8999.50, category="Furniture"),
            Product(name="Sofa Set", price=24999.00, category="Furniture"),
            Product(name="Table Lamp", price=1299.00, category="Lighting"),
            Product(name="Bookshelf", price=4599.00, category="Storage")
        ]
        for product in sample_products:
            db.session.add(product)
        print("✅ Added 5 sample products")
    
    if Transaction.query.count() == 0:
        sample_transactions = [
            Transaction(type="sale", amount=2999.99, description="Chair sale to customer", date="2024-01-15"),
            Transaction(type="purchase", amount=1500.00, description="Wood purchase", date="2024-01-10"),
            Transaction(type="sale", amount=8999.50, description="Office desk sale", date="2024-01-20"),
            Transaction(type="purchase", amount=3200.00, description="Fabric purchase", date="2024-01-05")
        ]
        for transaction in sample_transactions:
            db.session.add(transaction)
        print("✅ Added 4 sample transactions")
    
    if Budget.query.count() == 0:
        sample_budgets = [
            Budget(name="Marketing", amount=50000, spent=32500),
            Budget(name="Production", amount=150000, spent=112500),
            Budget(name="Sales", amount=75000, spent=48000),
            Budget(name="R&D", amount=30000, spent=12500)
        ]
        for budget in sample_budgets:
            db.session.add(budget)
        print("✅ Added 4 sample budgets")
    
    db.session.commit()
    print("✅ Database ready with sample data")

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 SHIV FURNITURE BUDGET SYSTEM")
    print("📡 API Server: http://localhost:5000")
    print("🔗 Test: http://localhost:5000/api/test")
    print("=" * 60)
    print("📊 Available APIs:")
    print("   GET  /api/products         - List all products")
    print("   POST /api/products         - Create product")
    print("   GET  /api/transactions     - List all transactions")
    print("   POST /api/transactions     - Create transaction")
    print("   GET  /api/budgets          - List all budgets")
    print("   POST /api/budgets          - Create budget")
    print("   GET  /api/reports/budget-vs-actual - Budget report")
    print("=" * 60)
    app.run(debug=True, port=5000, use_reloader=False)