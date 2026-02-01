# backend/app/utils/json_response.py
"""Return JSON responses using json.dumps with a custom default so date/datetime always serialize."""
import json
from datetime import date, datetime
from flask import Response

try:
    from bson import ObjectId
except ImportError:
    ObjectId = None


def _json_default(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, date):
        return obj.isoformat()
    if ObjectId is not None and isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def json_response(data, status=200):
    """Serialize data to JSON with date/datetime/ObjectId support. Bypasses Flask jsonify."""
    body = json.dumps(data, default=_json_default)
    return Response(body, status=status, mimetype="application/json")
