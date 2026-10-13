"""
CareSync Operational Health & Metrics Blueprint
Used by Docker healthchecks, Jenkins CI/CD verification stages, and uptime monitors.
"""
import time
from datetime import datetime
from flask import Blueprint, jsonify
from app.db import get_db

health_bp = Blueprint('health', __name__)
START_TIME = time.time()


@health_bp.route('/health', methods=['GET'])
def health():
    """Liveness probe: verifies that the web service is responsive."""
    return jsonify({
        'status': 'healthy',
        'application': 'CareSync',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), 200


@health_bp.route('/health/ready', methods=['GET'])
def readiness():
    """Readiness probe: validates SQLite database connectivity."""
    try:
        db = get_db()
        db.execute("SELECT 1").fetchone()
        return jsonify({
            'status': 'ready',
            'application': 'CareSync',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
    except Exception as exc:
        return jsonify({
            'status': 'unhealthy',
            'application': 'CareSync',
            'database': 'error',
            'error': str(exc),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 503


@health_bp.route('/metrics', methods=['GET'])
@health_bp.route('/health/metrics', methods=['GET'])
def metrics():
    """Basic operational metrics for deployment verification and monitoring."""
    uptime_seconds = int(time.time() - START_TIME)
    try:
        db = get_db()
        user_count = db.execute("SELECT COUNT(*) AS c FROM users").fetchone()['c']
        app_count = db.execute("SELECT COUNT(*) AS c FROM appointments").fetchone()['c']
        doc_count = db.execute("SELECT COUNT(*) AS c FROM doctors").fetchone()['c']
        db_status = "operational"
    except Exception:
        user_count = -1
        app_count = -1
        doc_count = -1
        db_status = "unreachable"

    return jsonify({
        'uptime_seconds': uptime_seconds,
        'database_status': db_status,
        'total_registered_users': user_count,
        'total_doctors': doc_count,
        'total_appointments_logged': app_count,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), 200
