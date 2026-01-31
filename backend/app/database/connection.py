# backend/app/database/connection.py
from flask_sqlalchemy import SQLAlchemy

# Create SQLAlchemy instance
db = SQLAlchemy()

def init_db(app):
    """Initialize database with app context"""
    db.init_app(app)
    return db