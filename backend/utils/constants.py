from enum import Enum

class Constants:
    """Application constants"""
    
    # Application
    APP_NAME = "Shiv Furniture Budget System"
    APP_VERSION = "1.0.0"
    
    # Roles
    class Roles(str, Enum):
        ADMIN = "admin"
        MANAGER = "manager"
        ACCOUNTANT = "accountant"
        SALES = "sales"
        PURCHASE = "purchase"
        CUSTOMER = "customer"
        VENDOR = "vendor"
    
    # Status Codes
    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_DRAFT = "draft"
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    
    # Transaction Types
    class TransactionTypes(str, Enum):
        PURCHASE_ORDER = "purchase_order"
        SALES_ORDER = "sales_order"
        PURCHASE_INVOICE = "purchase_invoice"
        SALES_INVOICE = "sales_invoice"
        PAYMENT_IN = "payment_in"
        PAYMENT_OUT = "payment_out"
        JOURNAL_ENTRY = "journal_entry"
    
    # Invoice Types
    class InvoiceTypes(str, Enum):
        SALES = "sales"
        PURCHASE = "purchase"
        CREDIT_NOTE = "credit_note"
        DEBIT_NOTE = "debit_note"
    
    # Payment Methods
    class PaymentMethods(str, Enum):
        CASH = "cash"
        CHEQUE = "cheque"
        BANK_TRANSFER = "bank_transfer"
        CREDIT_CARD = "credit_card"
        DEBIT_CARD = "debit_card"
        UPI = "upi"
        ONLINE = "online"
    
    # Budget Periods
    class BudgetPeriods(str, Enum):
        DAILY = "daily"
        WEEKLY = "weekly"
        MONTHLY = "monthly"
        QUARTERLY = "quarterly"
        HALF_YEARLY = "half_yearly"
        YEARLY = "yearly"
        CUSTOM = "custom"
    
    # Supported Currencies
    SUPPORTED_CURRENCIES = ['INR', 'USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD']
    
    # Tax Types
    class TaxTypes(str, Enum):
        GST = "gst"
        VAT = "vat"
        SGST = "sgst"
        CGST = "cgst"
        IGST = "igst"
        CUSTOM = "custom"
    
    # Default GST Rates (India)
    GST_RATES = {
        '0%': 0.0,
        '5%': 5.0,
        '12%': 12.0,
        '18%': 18.0,
        '28%': 28.0
    }
    
    # Product Categories
    PRODUCT_CATEGORIES = [
        'furniture',
        'wood',
        'metal',
        'fabric',
        'tools',
        'electronics',
        'packaging',
        'other'
    ]
    
    # Units of Measure
    UNITS_OF_MEASURE = [
        'pcs', 'kg', 'g', 'l', 'ml', 'm', 'cm', 'mm',
        'sqm', 'sqft', 'box', 'pack', 'roll', 'set'
    ]
    
    # Auto-Analytical Condition Operators
    CONDITION_OPERATORS = [
        'equals',
        'not_equals',
        'contains',
        'starts_with',
        'ends_with',
        'greater_than',
        'less_than',
        'between',
        'in_list'
    ]
    
    # Condition Fields
    CONDITION_FIELDS = [
        'product_category',
        'product_name',
        'contact_type',
        'transaction_type',
        'amount',
        'date'
    ]
    
    # File upload
    MAX_FILE_SIZE_MB = 10
    ALLOWED_FILE_EXTENSIONS = {
        'images': ['.jpg', '.jpeg', '.png', '.gif'],
        'documents': ['.pdf', '.doc', '.docx', '.xls', '.xlsx'],
        'all': ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.xls', '.xlsx']
    }
    
    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # Date Formats
    DATE_FORMAT = "%Y-%m-%d"
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    DISPLAY_DATE_FORMAT = "%d %b, %Y"
    
    # Response Messages
    class Messages(str, Enum):
        SUCCESS = "Operation completed successfully"
        CREATED = "Record created successfully"
        UPDATED = "Record updated successfully"
        DELETED = "Record deleted successfully"
        NOT_FOUND = "Record not found"
        UNAUTHORIZED = "Unauthorized access"
        FORBIDDEN = "Access forbidden"
        VALIDATION_ERROR = "Validation failed"
        SERVER_ERROR = "Internal server error"
        DUPLICATE_ERROR = "Duplicate record found"
    
    # Error Codes
    class ErrorCodes(int, Enum):
        VALIDATION_ERROR = 400
        UNAUTHORIZED = 401
        FORBIDDEN = 403
        NOT_FOUND = 404
        DUPLICATE_ERROR = 409
        SERVER_ERROR = 500