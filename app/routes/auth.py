"""
CareSync Authentication Blueprint
Handles user login, registration, logout, session state, and RBAC decorators.
"""
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g
from app.models import (
    verify_user_credentials, create_user, get_user_by_id,
    get_user_by_username, get_user_by_email, update_user_profile,
    log_activity
)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(f):
    """Decorator to enforce authenticated session."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """Decorator to enforce role-based access control (RBAC)."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Please sign in to access this page.", "warning")
                return redirect(url_for('auth.login', next=request.url))
            if session.get('role') not in roles:
                flash("Access denied. You do not have permissions for this resource.", "danger")
                return render_template('errors/403.html'), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login with credential validation and role-based redirection."""
    if 'user_id' in session:
        role = session.get('role')
        if role == 'admin':
            return redirect(url_for('dashboard.admin_dashboard'))
        elif role == 'doctor':
            return redirect(url_for('dashboard.doctor_dashboard'))
        else:
            return redirect(url_for('dashboard.patient_dashboard'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')

        if not identifier or not password:
            flash("Please provide both username/email and password.", "danger")
            return render_template('auth/login.html')

        user = verify_user_credentials(identifier, password)
        if not user:
            flash("Invalid credentials or account inactive. Please check and retry.", "danger")
            return render_template('auth/login.html')

        # Establish secure session
        session.clear()
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['full_name'] = user['full_name']
        session['role'] = user['role']
        session.permanent = True

        log_activity(user['id'], 'LOGIN', f"User {user['username']} logged in", request.remote_addr)
        flash(f"Welcome back, {user['full_name']}!", "success")

        next_url = request.args.get('next')
        if next_url and next_url.startswith('/'):
            return redirect(next_url)

        if user['role'] == 'admin':
            return redirect(url_for('dashboard.admin_dashboard'))
        elif user['role'] == 'doctor':
            return redirect(url_for('dashboard.doctor_dashboard'))
        else:
            return redirect(url_for('dashboard.patient_dashboard'))

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Patient self-registration."""
    if 'user_id' in session:
        return redirect(url_for('dashboard.patient_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        email = request.form.get('email', '').strip().lower()
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validations
        if not username or len(username) < 3:
            flash("Username must be at least 3 characters.", "danger")
            return render_template('auth/register.html')
        if not email or '@' not in email:
            flash("Please provide a valid email address.", "danger")
            return render_template('auth/register.html')
        if not full_name:
            flash("Full name is required.", "danger")
            return render_template('auth/register.html')
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template('auth/register.html')
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('auth/register.html')

        # Uniqueness checks
        if get_user_by_username(username):
            flash("Username already exists. Please pick another.", "warning")
            return render_template('auth/register.html')
        if get_user_by_email(email):
            flash("An account with this email address already exists.", "warning")
            return render_template('auth/register.html')

        # Create patient account
        user_id = create_user(username, email, password, role='patient', full_name=full_name, phone=phone)
        log_activity(user_id, 'REGISTER', f"New patient registration: {username}", request.remote_addr)
        flash("Registration successful! You may now sign in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
def logout():
    """Clear session and log activity."""
    user_id = session.get('user_id')
    username = session.get('username', 'Guest')
    if user_id:
        log_activity(user_id, 'LOGOUT', f"User {username} logged out", request.remote_addr)
    session.clear()
    flash("You have successfully signed out.", "info")
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """View and update user profile."""
    user = get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        if not full_name:
            flash("Full name cannot be empty.", "danger")
        else:
            update_user_profile(user['id'], full_name, phone)
            session['full_name'] = full_name
            log_activity(user['id'], 'PROFILE_UPDATE', "Profile details updated", request.remote_addr)
            flash("Profile updated successfully.", "success")
            return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html', user=user)
