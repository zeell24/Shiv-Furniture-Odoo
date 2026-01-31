from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum
from bson import ObjectId
from pydantic import BaseModel, Field, validator, EmailStr
from .connection import get_db

# Custom ObjectId type for Pydantic
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

# Enums
class ContactType(str, Enum):
    CUSTOMER = "customer"
    VENDOR = "vendor"
    EMPLOYEE = "employee"

class TransactionType(str, Enum):
    PURCHASE = "purchase"
    SALE = "sale"
    EXPENSE = "expense"
    INCOME = "income"

class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentMethod(str, Enum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CHEQUE = "cheque"
    ONLINE = "online"
    CREDIT_CARD = "credit_card"

class BudgetStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"
    ARCHIVED = "archived"

# Base Model with common fields
class BaseDBModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        use_enum_values = True

# User Model (for Admin/Portal users)
class User(BaseDBModel):
    username: str
    email: EmailStr
    password_hash: str
    full_name: str
    role: str = "user"  # admin, manager, user, portal_user
    contact_id: Optional[PyObjectId] = None
    last_login: Optional[datetime] = None
    
    class Collection:
        name = "users"

# Contact Model
class Contact(BaseDBModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    contact_type: ContactType
    tax_id: Optional[str] = None
    credit_limit: Optional[float] = 0.0
    current_balance: float = 0.0
    notes: Optional[str] = None
    
    class Collection:
        name = "contacts"

# Product Model
class Product(BaseDBModel):
    sku: str
    name: str
    description: Optional[str] = None
    category: str
    unit_price: float
    cost_price: Optional[float] = None
    current_stock: float = 0
    min_stock: float = 0
    max_stock: Optional[float] = None
    unit_of_measure: str = "pcs"
    is_active: bool = True
    
    class Collection:
        name = "products"

# Analytical Account (Cost Center) Model
class AnalyticalAccount(BaseDBModel):
    code: str
    name: str
    description: Optional[str] = None
    parent_id: Optional[PyObjectId] = None
    parent_code: Optional[str] = None
    level: int = 1
    is_group: bool = False
    budget_allowed: bool = True
    
    class Collection:
        name = "analytical_accounts"

# Auto-Analytical Model (Rules)
class AutoAnalyticalModel(BaseDBModel):
    name: str
    description: Optional[str] = None
    conditions: List[Dict[str, Any]]  # List of condition rules
    analytical_account_id: PyObjectId
    priority: int = 1
    is_active: bool = True
    
    class Collection:
        name = "auto_analytical_models"

# Budget Model
class Budget(BaseDBModel):
    name: str
    description: Optional[str] = None
    analytical_account_id: PyObjectId
    start_date: date
    end_date: date
    allocated_amount: float
    currency: str = "INR"
    status: BudgetStatus = BudgetStatus.DRAFT
    actual_amount: float = 0.0
    remaining_amount: float = Field(default_factory=lambda: None)
    achievement_percentage: float = 0.0
    
    @validator('remaining_amount', pre=True, always=True)
    def calculate_remaining(cls, v, values):
        if v is None and 'allocated_amount' in values:
            return values['allocated_amount'] - values.get('actual_amount', 0)
        return v
    
    class Collection:
        name = "budgets"

# Transaction Model
class Transaction(BaseDBModel):
    transaction_number: str
    transaction_date: date
    type: TransactionType
    contact_id: Optional[PyObjectId] = None
    analytical_account_id: Optional[PyObjectId] = None
    description: Optional[str] = None
    total_amount: float
    tax_amount: float = 0.0
    net_amount: float
    currency: str = "INR"
    status: str = "posted"
    reference_number: Optional[str] = None
    items: List[Dict[str, Any]] = []  # Line items
    
    class Collection:
        name = "transactions"

# Invoice Model
class Invoice(BaseDBModel):
    invoice_number: str
    invoice_date: date
    due_date: date
    contact_id: PyObjectId
    transaction_id: Optional[PyObjectId] = None
    analytical_account_id: Optional[PyObjectId] = None
    sub_total: float
    tax_amount: float
    total_amount: float
    paid_amount: float = 0.0
    due_amount: float = Field(default_factory=lambda: None)
    status: InvoiceStatus = InvoiceStatus.DRAFT
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    items: List[Dict[str, Any]] = []
    
    @validator('due_amount', pre=True, always=True)
    def calculate_due(cls, v, values):
        if v is None and 'total_amount' in values:
            return values['total_amount'] - values.get('paid_amount', 0)
        return v
    
    class Collection:
        name = "invoices"

# Payment Model
class Payment(BaseDBModel):
    payment_number: str
    payment_date: date
    contact_id: PyObjectId
    invoice_id: Optional[PyObjectId] = None
    transaction_id: Optional[PyObjectId] = None
    amount: float
    payment_method: PaymentMethod
    status: PaymentStatus = PaymentStatus.PENDING
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    bank_details: Optional[Dict[str, Any]] = None
    
    class Collection:
        name = "payments"

# Helper function to get collection
def get_collection(model_class):
    """Get MongoDB collection for a model class"""
    db = get_db()
    return db[model_class.Collection.name]