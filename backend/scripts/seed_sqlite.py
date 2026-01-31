#!/usr/bin/env python3
"""Seed SQLite database with cost centers and optional demo data."""

import sys
import os
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_seed():
    from app.main import create_app
    from app.database.connection import db
    from app.database.models import User, CostCenter, MasterBudget, Transaction

    app = create_app()
    with app.app_context():
        db.create_all()

        # Seed cost centers (matching analytical rules)
        centers = [
            {'name': 'Production', 'code': 'PROD', 'description': 'Wood, timber, plywood, manufacturing'},
            {'name': 'Marketing', 'code': 'MKT', 'description': 'Expo, fair, advertisement, social, marketing'},
            {'name': 'Logistics', 'code': 'LOG', 'description': 'Delivery, fuel, truck, shipping, freight'},
            {'name': 'Administrative', 'code': 'ADMIN', 'description': 'Office, stationary, rent, electricity'},
            {'name': 'Furniture Expo 2026', 'code': 'EXPO26', 'description': 'Default/uncategorized'},
        ]
        for c in centers:
            if not CostCenter.query.filter_by(code=c['code']).first():
                cc = CostCenter(name=c['name'], code=c['code'], description=c.get('description', ''))
                db.session.add(cc)
                print(f"  Created cost center: {c['name']} ({c['code']})")

        # Master budget
        if not MasterBudget.query.first():
            db.session.add(MasterBudget(amount=1500000))
            print("  Created master budget: ₹15,00,000")

        # Admin user
        if not User.query.filter_by(email='admin@shivfurniture.com').first():
            admin = User(email='admin@shivfurniture.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            print("  Created admin user: admin@shivfurniture.com / admin123")

        db.session.commit()
        print("\n✅ SQLite seed completed.")

if __name__ == '__main__':
    run_seed()
