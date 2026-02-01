#!/usr/bin/env python3
"""Seed MongoDB with cost centers, admin user, and master budget."""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.models import user_set_password


def run_seed():
    from app.main import create_app
    from app.database.connection import get_db

    app = create_app()
    with app.app_context():
        db = get_db()

        centers = [
            {'name': 'Production', 'code': 'PROD', 'description': 'Wood, timber, plywood, manufacturing'},
            {'name': 'Marketing', 'code': 'MKT', 'description': 'Expo, fair, advertisement, social, marketing'},
            {'name': 'Logistics', 'code': 'LOG', 'description': 'Delivery, fuel, truck, shipping, freight'},
            {'name': 'Administrative', 'code': 'ADMIN', 'description': 'Office, stationary, rent, electricity'},
            {'name': 'Furniture Expo 2026', 'code': 'EXPO26', 'description': 'Default/uncategorized'},
        ]
        for c in centers:
            if not db.cost_centers.find_one({'code': c['code']}):
                db.cost_centers.insert_one({
                    'name': c['name'],
                    'code': c['code'],
                    'description': c.get('description', ''),
                    'created_at': datetime.utcnow()
                })
                print(f"  Created cost center: {c['name']} ({c['code']})")

        if not db.master_budget.find_one({}):
            db.master_budget.insert_one({'amount': 1500000, 'updated_at': datetime.utcnow()})
            print("  Created master budget: ₹15,00,000")

        if not db.users.find_one({'email': 'admin@shivfurniture.com'}):
            db.users.insert_one({
                'email': 'admin@shivfurniture.com',
                'role': 'admin',
                'password_hash': user_set_password('admin123'),
                'created_at': datetime.utcnow()
            })
            print("  Created admin user: admin@shivfurniture.com / admin123")

        print("\n✅ MongoDB seed completed.")


if __name__ == '__main__':
    run_seed()
