"""
CareSync Application Entry Point
Supports running in local development mode or via WSGI servers (Gunicorn / Waitress).
"""
import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() in ['true', '1', 't']
    print(f"Starting CareSync on http://localhost:{port} (debug={debug})...")
    app.run(host='0.0.0.0', port=port, debug=debug)
