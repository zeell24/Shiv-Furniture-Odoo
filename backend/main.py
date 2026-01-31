"""
Backend entry point when run from backend directory: python main.py
"""
import sys
import os

backend_root = os.path.dirname(os.path.abspath(__file__))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from app.main import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 50)
    print("Shiv Furniture Budget API (main.py)")
    print("Server: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000, host='0.0.0.0')
