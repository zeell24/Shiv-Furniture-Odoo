"""
Backend entry point. Run from project root or backend directory:
  python backend/run.py
  cd backend && python run.py
"""
import sys
import os

# Add backend root to Python path so 'app' package resolves
backend_root = os.path.dirname(os.path.abspath(__file__))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

# Optional: use .env from project root (one level up)
project_root = os.path.dirname(backend_root)
env_path = os.path.join(project_root, '.env')
if os.path.isfile(env_path):
    from dotenv import load_dotenv
    load_dotenv(env_path)

from app.main import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 50)
    print("Shiv Furniture Budget API")
    print("Server: http://localhost:5000")
    print("Health: http://localhost:5000/health")
    print("=" * 50)
    app.run(debug=True, port=5000, host='0.0.0.0')
