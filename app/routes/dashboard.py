"""
CareSync Dashboard Blueprint
Renders tailored dashboards for Admin, Doctor, and Patient roles
with real-time statistics computed directly from the SQLite database.
"""
from datetime import date
from flask import Blueprint, render_template, redirect, url_for, session, flash
from app.routes.auth import login_required, role_required
from app.models import (
    get_hospital_stats, list_recent_activity, list_appointments,
    get_doctor_by_user_id, get_doctor_stats, get_patient_stats,
    list_doctors, get_live_queue
)

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
@login_required
def index():
    """Route user to their role-specific dashboard."""
    role = session.get('role')
    if role == 'admin':
        return redirect(url_for('dashboard.admin_dashboard'))
    elif role == 'doctor':
        return redirect(url_for('dashboard.doctor_dashboard'))
    return redirect(url_for('dashboard.patient_dashboard'))


@dashboard_bp.route('/admin')
@role_required('admin')
def admin_dashboard():
    """Admin Dashboard: Global metrics, recent bookings, live queue, audit activity."""
    stats = get_hospital_stats()
    today_str = date.today().strftime("%Y-%m-%d")
    recent_appointments = list_appointments(app_date=today_str)
    # If today has no appointments yet, show the latest overall appointments
    if not recent_appointments:
        recent_appointments = list_appointments()[:10]

    activities = list_recent_activity(limit=8)
    doctors = list_doctors()[:6]
    live_queue = get_live_queue(today_str)[:8]

    return render_template(
        'dashboard/admin.html',
        stats=stats,
        appointments=recent_appointments,
        activities=activities,
        doctors=doctors,
        live_queue=live_queue,
        today=today_str
    )


@dashboard_bp.route('/doctor')
@role_required('doctor')
def doctor_dashboard():
    """Doctor Dashboard: Assigned appointments, queue tokens, patient statuses."""
    doc = get_doctor_by_user_id(session['user_id'])
    if not doc:
        flash("Doctor profile not found for this user account.", "danger")
        return redirect(url_for('auth.logout'))

    stats = get_doctor_stats(doc['id'])
    today_str = date.today().strftime("%Y-%m-%d")
    today_appointments = list_appointments(doctor_id=doc['id'], app_date=today_str)
    all_appointments = list_appointments(doctor_id=doc['id'])[:10]
    live_queue = get_live_queue(today_str, doctor_id=doc['id'])

    return render_template(
        'dashboard/doctor.html',
        doctor=doc,
        stats=stats,
        today_appointments=today_appointments,
        all_appointments=all_appointments,
        live_queue=live_queue,
        today=today_str
    )


@dashboard_bp.route('/patient')
@role_required('patient')
def patient_dashboard():
    """Patient Dashboard: Upcoming appointments, past medical visits, quick booking."""
    user_id = session['user_id']
    stats = get_patient_stats(user_id)
    today_str = date.today().strftime("%Y-%m-%d")
    my_appointments = list_appointments(patient_id=user_id)

    upcoming = [a for a in my_appointments if a['appointment_date'] >= today_str and a['status'] in ['Confirmed', 'Checked In']]
    past = [a for a in my_appointments if a['appointment_date'] < today_str or a['status'] in ['Completed', 'Cancelled']]

    doctors = list_doctors(available_only=True)[:4]

    return render_template(
        'dashboard/patient.html',
        stats=stats,
        upcoming_appointments=upcoming,
        past_appointments=past,
        doctors=doctors,
        today=today_str
    )
