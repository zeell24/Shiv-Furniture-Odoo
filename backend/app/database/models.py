# backend/app/database/models.py
from app.database.connection import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer')  # 'admin' or 'customer'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    invoices = db.relationship('Invoice', backref='customer', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CostCenter(db.Model):
    """Analytical accounts / cost centers"""
    __tablename__ = 'cost_centers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    budgets = db.relationship('Budget', backref='cost_center', lazy=True)
    transactions = db.relationship('Transaction', backref='cost_center', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Product(db.Model):
    """Product master data"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    sku = db.Column(db.String(50), unique=True)
    category = db.Column(db.String(100))
    price = db.Column(db.Float, nullable=False, default=0.0)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='product', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'sku': self.sku,
            'category': self.category,
            'price': self.price,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Budget(db.Model):
    """Budget definition"""
    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    cost_center_id = db.Column(db.Integer, db.ForeignKey('cost_centers.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'cost_center_id': self.cost_center_id,
            'cost_center_name': self.cost_center.name if self.cost_center else None,
            'amount': self.amount,
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Transaction(db.Model):
    """Purchase/Sales transactions"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # 'purchase' or 'sale'
    amount = db.Column(db.Float, nullable=False)
    cost_center_id = db.Column(db.Integer, db.ForeignKey('cost_centers.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, default=1)
    description = db.Column(db.Text)
    transaction_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'amount': self.amount,
            'cost_center_id': self.cost_center_id,
            'cost_center_name': self.cost_center.name if self.cost_center else None,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'quantity': self.quantity,
            'description': self.description,
            'transaction_date': self.transaction_date.isoformat(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Invoice(db.Model):
    """Customer invoices"""
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='unpaid')  # 'unpaid', 'partial', 'paid'
    due_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    payments = db.relationship('Payment', backref='invoice', lazy=True)
    
    def to_dict(self):
        # Calculate paid amount
        paid_amount = sum(payment.amount for payment in self.payments)
        
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'customer_id': self.customer_id,
            'customer_email': self.customer.email if self.customer else None,
            'amount': self.amount,
            'paid_amount': paid_amount,
            'balance': self.amount - paid_amount,
            'status': self.status,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Payment(db.Model):
    """Payment records"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50))  # 'stripe', 'cash', 'bank_transfer'
    transaction_id = db.Column(db.String(100))  # External transaction ID
    status = db.Column(db.String(20), default='pending')  # 'pending', 'completed', 'failed'
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'invoice_number': self.invoice.invoice_number if self.invoice else None,
            'amount': self.amount,
            'payment_method': self.payment_method,
            'transaction_id': self.transaction_id,
            'status': self.status,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }