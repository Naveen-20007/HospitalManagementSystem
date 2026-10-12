"""
CareSync Doctors Management Blueprint
Handles doctor listings, specialty filtering, profile updates, and working schedules.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.routes.auth import login_required, role_required
from app.models import (
    list_doctors, get_doctor_by_id, update_doctor,
    set_doctor_availability, get_doctor_availability,
    create_user, create_doctor, get_user_by_username,
    log_activity
)

doctors_bp = Blueprint('doctors', __name__, url_prefix='/doctors')


@doctors_bp.route('/')
@login_required
def index():
    """Browse doctor directory with specialty and search filters."""
    specialty = request.args.get('specialty', '').strip()
    search = request.args.get('search', '').strip()

    doctors = list_doctors(specialty=specialty if specialty else None, search=search if search else None)
    all_specialties = ["Cardiology", "Neurology", "Pediatrics", "Orthopedics", "Dermatology", "General Medicine", "Oncology", "ENT"]

    return render_template(
        'doctors/index.html',
        doctors=doctors,
        specialties=all_specialties,
        selected_specialty=specialty,
        search_query=search
    )


@doctors_bp.route('/<int:doctor_id>')
@login_required
def detail(doctor_id):
    """View doctor profile, working hours, and book button."""
    doc = get_doctor_by_id(doctor_id)
    if not doc:
        flash("Doctor record not found.", "warning")
        return redirect(url_for('doctors.index'))

    availability = get_doctor_availability(doctor_id)
    return render_template('doctors/detail.html', doctor=doc, availability=availability)


@doctors_bp.route('/manage', methods=['GET', 'POST'])
@role_required('admin')
def manage():
    """Admin view: List all doctors and create new doctor accounts."""
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        username = request.form.get('username', '').strip().lower()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', 'Doctor@123')
        doctor_code = request.form.get('doctor_code', '').strip().upper()
        specialty = request.form.get('specialty', '').strip()
        qualification = request.form.get('qualification', '').strip()
        consultation_fee = request.form.get('consultation_fee', '500')
        department = request.form.get('department', 'Outpatient').strip()
        phone = request.form.get('phone', '').strip()

        if not full_name or not username or not email or not doctor_code or not specialty:
            flash("All doctor required fields must be filled.", "danger")
        elif get_user_by_username(username):
            flash("Username already taken. Please choose another.", "warning")
        else:
            user_id = create_user(username, email, password, role='doctor', full_name=full_name, phone=phone)
            doc_id = create_doctor(user_id, doctor_code, specialty, qualification, consultation_fee, department)

            # Set standard default availability (Monday to Saturday, 09:00 - 17:00)
            weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            for day in weekdays:
                set_doctor_availability(doc_id, day, "09:00", "17:00", 30)

            log_activity(session['user_id'], 'CREATE_DOCTOR', f"Created doctor {full_name} ({doctor_code})", request.remote_addr)
            flash(f"Doctor {full_name} ({doctor_code}) created successfully with default schedule.", "success")
            return redirect(url_for('doctors.manage'))

    doctors = list_doctors()
    return render_template('doctors/manage.html', doctors=doctors)


@doctors_bp.route('/<int:doctor_id>/edit', methods=['GET', 'POST'])
@role_required('admin')
def edit(doctor_id):
    """Admin view: Edit doctor details and toggle availability."""
    doc = get_doctor_by_id(doctor_id)
    if not doc:
        flash("Doctor not found.", "warning")
        return redirect(url_for('doctors.manage'))

    if request.method == 'POST':
        specialty = request.form.get('specialty', '').strip()
        qualification = request.form.get('qualification', '').strip()
        consultation_fee = float(request.form.get('consultation_fee', 500))
        department = request.form.get('department', '').strip()
        is_available = bool(request.form.get('is_available'))

        update_doctor(doctor_id, specialty, qualification, consultation_fee, department, is_available)
        log_activity(session['user_id'], 'UPDATE_DOCTOR', f"Updated doctor {doc['full_name']}", request.remote_addr)
        flash("Doctor details updated successfully.", "success")
        return redirect(url_for('doctors.manage'))

    availability = get_doctor_availability(doctor_id)
    return render_template('doctors/edit.html', doctor=doc, availability=availability)


@doctors_bp.route('/<int:doctor_id>/availability', methods=['POST'])
@role_required('admin', 'doctor')
def update_schedule(doctor_id):
    """Update working hours for a specific weekday."""
    day = request.form.get('day_of_week')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    duration = int(request.form.get('slot_duration_mins', 30))

    if day and start_time and end_time:
        set_doctor_availability(doctor_id, day, start_time, end_time, duration)
        log_activity(session['user_id'], 'UPDATE_SCHEDULE', f"Updated schedule for Doc #{doctor_id} on {day}", request.remote_addr)
        flash(f"Updated schedule for {day} ({start_time} - {end_time}).", "success")

    return redirect(request.referrer or url_for('doctors.index'))
