# Shiv Furniture ERP - Setup Guide

## Prerequisites
- Node.js (for frontend)
- Python 3.x (for backend)

## Backend Setup

```bash
cd backend
pip install -r requirements.txt
python run.py
```

Or with Flask app directly:
```bash
cd backend
pip install -r requirements.txt
python -m flask --app app.main:create_app run --port 5000
```

### Database (MongoDB – online)
- Backend uses **MongoDB** (e.g. MongoDB Atlas). You must set this in `.env` (in project root or in `backend/`):
  - `MONGO_URI` – connection string (e.g. `mongodb+srv://user:pass@cluster.mongodb.net/`)
  - `MONGO_DB_NAME` – database name (e.g. `shiv_furniture_db`)
- **"Connection refused" / "Could not connect to MongoDB"** means no MongoDB is running on localhost and `MONGO_URI` is not set. Create a `.env` file (copy from `.env.example`) and set `MONGO_URI` to your [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) connection string.

### Seed Database (Creates cost centers, admin user, master budget)
Run after first start so APIs return data:
```bash
cd backend
python scripts/seed_sqlite.py
```
Or from project root: `python backend/scripts/seed_sqlite.py`

**Demo Login:** `admin@shivfurniture.com` / `admin123`

## Frontend Setup

```bash
cd frontend/dashboard-app
npm install
npm run dev
```

The app will auto-login with demo credentials on first load.

## Features Integrated

1. **Financial Hub (Dashboard)** - Real-time budget monitoring, chart from DB data only (empty when no transactions)
2. **Transactions** - Add expenses with auto-categorization (Production, Marketing, Logistics, etc.)
3. **Budgets** - Per cost-center budgets with utilization tracking
4. **Reports** - Budget vs Actual, downloadable report, chart from transactions
5. **Customer Portal** - View transactions, Settle Balance, Stripe-style checkout
6. **Payment Overview** - Actual vs remaining budget from database

## Chart Behavior
- **Empty by default** - No hardcoded data
- **Populates from database** - Add transactions to see the expense chart
- Reports and Dashboard both use real transaction data
