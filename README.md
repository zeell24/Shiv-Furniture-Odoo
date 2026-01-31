# Shiv-Furniture-Odoo
A centralized budget accounting system that tracks transactions cost-center wise, monitors budget vs actual performance in real time, and provides automated reporting and customer portal access for better financial control.

## Project structure
- **backend/** – Flask API (SQLAlchemy, JWT). Entry: `run.py` or `main.py`.
- **frontend/dashboard-app/** – Main React (Vite) app. API calls go to backend via proxy in dev.
- **frontend/invoice-portal/** – Separate invoice portal app (optional).
- Loose JS/TS files in **frontend/** root are legacy; their logic lives in `dashboard-app/src` (utils, hooks, components).

## How to run

### Backend (from project root or backend folder)
```bash
# From project root
python backend/run.py

# Or from backend folder
cd backend
python run.py
# or: python main.py
```
API: http://localhost:5000  
Health: http://localhost:5000/health

### Frontend (main app)
```bash
cd frontend/dashboard-app
npm install
npm run dev
```
App: http://localhost:5173  
In dev, `/api` is proxied to the backend so the app talks to http://localhost:5000/api.

### Connect frontend to backend
1. Start the backend first (port 5000).
2. Start the frontend (`npm run dev` in `frontend/dashboard-app`).
3. Log in via the app (or register at `/api/auth/register`) so API requests include the JWT; the frontend sends the token from `localStorage.token` automatically.
