# backend/app/database/models.py - MongoDB document helpers (no SQLAlchemy)
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId


def _id_str(doc):
    """Add 'id' as string from '_id' for API responses."""
    if doc is None:
        return None
    d = dict(doc)
    if '_id' in d:
        d['id'] = str(d['_id'])
        del d['_id']
    return d


def _serialize_dates(d):
    """Convert datetime/date to ISO string for JSON (handles nested dicts/lists)."""
    if d is None:
        return d
    for k, v in list(d.items()):
        if isinstance(v, datetime):
            d[k] = v.isoformat()
        elif isinstance(v, date) and not isinstance(v, datetime):
            d[k] = v.isoformat()
        elif isinstance(v, dict):
            _serialize_dates(v)
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, (datetime, date)):
                    v[i] = item.isoformat()
                elif isinstance(item, dict):
                    _serialize_dates(item)
    return d


# ---------- User ----------
def user_to_dict(doc):
    if not doc:
        return None
    d = _id_str(doc)
    _serialize_dates(d)
    d.pop('password_hash', None)
    return d


def user_check_password(password_hash, password):
    return check_password_hash(password_hash, password)


def user_set_password(password):
    return generate_password_hash(password)


# ---------- CostCenter ----------
def cost_center_to_dict(doc):
    if not doc:
        return None
    d = _id_str(doc)
    _serialize_dates(d)
    return d


# ---------- Product ----------
def product_to_dict(doc):
    if not doc:
        return None
    d = _id_str(doc)
    _serialize_dates(d)
    return d


# ---------- Budget ----------
def budget_to_dict(doc, cost_center_name=None):
    if not doc:
        return None
    d = _id_str(doc)
    _serialize_dates(d)
    if cost_center_name is not None:
        d['cost_center_name'] = cost_center_name
    return d


# ---------- MasterBudget ----------
def master_budget_to_dict(doc):
    if not doc:
        return None
    d = _id_str(doc)
    _serialize_dates(d)
    return d


# ---------- Transaction ----------
def transaction_to_dict(doc, cost_center_name=None, product_name=None):
    if not doc:
        return None
    d = _id_str(doc)
    _serialize_dates(d)
    if cost_center_name is not None:
        d['cost_center_name'] = cost_center_name
    if product_name is not None:
        d['product_name'] = product_name
    return d


# ---------- Invoice ----------
def invoice_to_dict(doc, customer_email=None, paid_amount=0):
    if not doc:
        return None
    d = _id_str(doc)
    _serialize_dates(d)
    if customer_email is not None:
        d['customer_email'] = customer_email
    d['paid_amount'] = paid_amount
    d['balance'] = d.get('amount', 0) - paid_amount
    return d


# ---------- Payment ----------
def payment_to_dict(doc, invoice_number=None):
    if not doc:
        return None
    d = _id_str(doc)
    _serialize_dates(d)
    if invoice_number is not None:
        d['invoice_number'] = invoice_number
    return d


def oid(s):
    """Convert string to ObjectId; return None if invalid."""
    if s is None:
        return None
    try:
        return ObjectId(s)
    except Exception:
        return None


def sanitize_for_json(obj):
    """Return a JSON-serializable copy: date/datetime -> ISO string, ObjectId -> str. Use before jsonify."""
    if obj is None:
        return None
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, date) and not isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [sanitize_for_json(v) for v in obj]
    if isinstance(obj, ObjectId):
        return str(obj)
    return obj
