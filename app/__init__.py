"""
CareSync Application Factory Module
Initializes Flask app, registers blueprints, connects database teardown,
and sets up global error handlers and template contexts.
"""
import os
from flask import Flask, render_template, redirect, url_for, session
from app.db import close_db, init_db, DEFAULT_DB_PATH
from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.doctors import doctors_bp
from app.routes.appointments import appointments_bp
from app.routes.queue import queue_bp
from app.routes.reports import reports_bp
from app.routes.health import health_bp
from app.routes.api import api_bp


def create_app(test_config=None):
    """Factory function for creating and configuring the Flask application instance."""
    app = Flask(__name__, instance_relative_config=True)

    # Default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'caresync-dev-secret-key-lab23it723-2026'),
        DATABASE=os.environ.get('DATABASE_PATH', DEFAULT_DB_PATH),
        APP_NAME='CareSync',
        APP_VERSION='1.0.0'
    )

    if test_config is not None:
        app.config.update(test_config)

    # Register database teardown
    app.teardown_appcontext(close_db)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(doctors_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(queue_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(api_bp)

    # Root route redirection
    @app.route('/')
    def root():
        if 'user_id' in session:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login'))

    # Custom Error Handlers
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # Global template context helpers
    @app.context_processor
    def inject_globals():
        return {
            'app_name': app.config['APP_NAME'],
            'app_version': app.config['APP_VERSION'],
            'current_user': {
                'id': session.get('user_id'),
                'username': session.get('username'),
                'full_name': session.get('full_name'),
                'role': session.get('role')
            } if 'user_id' in session else None
        }

    # Automatically ensure tables exist on first startup if file doesn't exist
    with app.app_context():
        db_path = app.config['DATABASE']
        if not os.path.exists(db_path):
            init_db(db_path)

    return app
