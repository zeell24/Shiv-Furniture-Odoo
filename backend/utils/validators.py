import re
from datetime import datetime, date
from typing import Any, Optional, Dict
from .constants import Constants

class Validators:
    """Collection of validation utilities"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number (basic validation)"""
        pattern = r'^[\d\s\-\+\(\)]{10,15}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def validate_date_range(start_date: date, end_date: date) -> bool:
        """Validate that start date is before end date"""
        return start_date <= end_date
    
    @staticmethod
    def validate_budget_amount(amount: float) -> bool:
        """Validate budget amount is positive"""
        return amount >= 0
    
    @staticmethod
    def validate_transaction_amount(amount: float) -> bool:
        """Validate transaction amount"""
        return amount > 0
    
    @staticmethod
    def validate_invoice_number(invoice_number: str) -> bool:
        """Validate invoice number format"""
        # Example: INV-2024-001
        pattern = r'^[A-Z]{3,5}-\d{4}-\d{3,6}$'
        return bool(re.match(pattern, invoice_number))
    
    @staticmethod
    def validate_sku(sku: str) -> bool:
        """Validate product SKU"""
        pattern = r'^[A-Z0-9\-]{5,20}$'
        return bool(re.match(pattern, sku))
    
    @staticmethod
    def validate_currency(currency: str) -> bool:
        """Validate currency code"""
        return currency.upper() in Constants.SUPPORTED_CURRENCIES
    
    @staticmethod
    def validate_percentage(value: float) -> bool:
        """Validate percentage value (0-100)"""
        return 0 <= value <= 100
    
    @staticmethod
    def validate_tax_id(tax_id: str, country_code: str = 'IN') -> bool:
        """Validate tax ID based on country"""
        if country_code == 'IN':
            # GST format validation
            pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
            return bool(re.match(pattern, tax_id.upper()))
        return True  # Basic validation for other countries
    
    @staticmethod
    def validate_json_schema(data: Dict, required_fields: list) -> bool:
        """Validate that required fields exist in data"""
        return all(field in data for field in required_fields)
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize input string to prevent injection"""
        if not text:
            return ""
        # Remove potentially dangerous characters
        return re.sub(r'[<>"\'\`;]', '', text).strip()
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validate password strength"""
        result = {
            'is_valid': True,
            'errors': []
        }
        
        if len(password) < 8:
            result['is_valid'] = False
            result['errors'].append('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', password):
            result['is_valid'] = False
            result['errors'].append('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', password):
            result['is_valid'] = False
            result['errors'].append('Password must contain at least one lowercase letter')
        
        if not re.search(r'[0-9]', password):
            result['is_valid'] = False
            result['errors'].append('Password must contain at least one number')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            result['is_valid'] = False
            result['errors'].append('Password must contain at least one special character')
        
        return result