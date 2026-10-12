"""
CareSync Appointments Blueprint
Handles booking workflow, double-booking validation, status transitions, and appointment details.
"""
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app.routes.auth import login_required, role_required
from app.models import (
    create_appointment, get_appointment_by_id, list_appointments,
    update_appointment_status, cancel_appointment, list_doctors,
    get_doctor_by_id, get_doctor_by_user_id, get_available_slots,
    log_activity
)

appointments_bp = Blueprint('appointments', __name__, url_prefix='/appointments')


@appointments_bp.route('/')
@login_required
def index():
    """List appointments according to role, with status, date, and keyword filters."""
    role = session['role']
    user_id = session['user_id']
    status_filter = request.args.get('status', '').strip()
    date_filter = request.args.get('date', '').strip()
    search = request.args.get('search', '').strip()

    if role == 'patient':
        appointments = list_appointments(
            patient_id=user_id,
            status=status_filter if status_filter else None,
            app_date=date_filter if date_filter else None,
            search=search if search else None
        )
    elif role == 'doctor':
        doc = get_doctor_by_user_id(user_id)
        doc_id = doc['id'] if doc else -1
        appointments = list_appointments(
            doctor_id=doc_id,
            status=status_filter if status_filter else None,
            app_date=date_filter if date_filter else None,
            search=search if search else None
        )
    else:  # Admin
        doctor_id_filter = request.args.get('doctor_id', type=int)
        appointments = list_appointments(
            doctor_id=doctor_id_filter,
            status=status_filter if status_filter else None,
            app_date=date_filter if date_filter else None,
            search=search if search else None
        )

    doctors = list_doctors() if role == 'admin' else []

    return render_template(
        'appointments/index.html',
        appointments=appointments,
        status_filter=status_filter,
        date_filter=date_filter,
        search=search,
        doctors=doctors
    )


@appointments_bp.route('/book', methods=['GET', 'POST'])
@login_required
def book():
    """Patient appointment booking with dynamic slot availability."""
    if request.method == 'POST':
        # Patient ID can be self (for patients) or chosen by Admin
        if session['role'] == 'patient':
            patient_id = session['user_id']
        else:
            patient_id = request.form.get('patient_id', type=int) or session['user_id']

        doctor_id = request.form.get('doctor_id', type=int)
        app_date = request.form.get('appointment_date', '').strip()
        time_slot = request.form.get('time_slot', '').strip()
        reason = request.form.get('reason', '').strip()

        if not doctor_id or not app_date or not time_slot or not reason:
            flash("Please complete all fields to book an appointment.", "danger")
            return redirect(url_for('appointments.book', doctor_id=doctor_id, date=app_date))

        app, err = create_appointment(patient_id, doctor_id, app_date, time_slot, reason)
        if err:
            flash(err, "danger")
            return redirect(url_for('appointments.book', doctor_id=doctor_id, date=app_date))

        log_activity(session['user_id'], 'BOOK_APPOINTMENT', f"Booked appointment {app['appointment_code']} with Doc #{doctor_id}", request.remote_addr)
        flash(f"Appointment booked successfully! Your reference code is {app['appointment_code']}.", "success")
        return redirect(url_for('appointments.detail', appointment_id=app['id']))

    # GET: render form
    preselected_doctor = request.args.get('doctor_id', type=int)
    preselected_date = request.args.get('date', date.today().strftime("%Y-%m-%d"))
    doctors = list_doctors(available_only=True)

    return render_template(
        'appointments/book.html',
        doctors=doctors,
        selected_doctor=preselected_doctor,
        selected_date=preselected_date,
        today=date.today().strftime("%Y-%m-%d")
    )


@appointments_bp.route('/slots')
@login_required
def get_slots():
    """API endpoint to get available slots for selected doctor and date."""
    doctor_id = request.args.get('doctor_id', type=int)
    app_date = request.args.get('date', '').strip()

    if not doctor_id or not app_date:
        return jsonify({'slots': [], 'error': 'doctor_id and date are required'}), 400

    slots = get_available_slots(doctor_id, app_date)
    return jsonify({'slots': slots, 'date': app_date, 'doctor_id': doctor_id})


@appointments_bp.route('/<int:appointment_id>')
@login_required
def detail(appointment_id):
    """View appointment card, confirmation details, and queue info."""
    app = get_appointment_by_id(appointment_id)
    if not app:
        flash("Appointment not found.", "warning")
        return redirect(url_for('appointments.index'))

    # Authorization
    role = session['role']
    user_id = session['user_id']
    if role == 'patient' and app['patient_id'] != user_id:
        flash("Unauthorized access to this appointment.", "danger")
        return render_template('errors/403.html'), 403

    if role == 'doctor':
        doc = get_doctor_by_user_id(user_id)
        if not doc or doc['id'] != app['doctor_id']:
            flash("Unauthorized access to this appointment.", "danger")
            return render_template('errors/403.html'), 403

    return render_template('appointments/detail.html', appointment=app)


@appointments_bp.route('/<int:appointment_id>/cancel', methods=['POST'])
@login_required
def cancel(appointment_id):
    """Cancel an appointment."""
    role = session['role']
    user_id = session['user_id']
    ok, err = cancel_appointment(appointment_id, user_id=user_id, role=role)
    if not ok:
        flash(err, "danger")
    else:
        log_activity(user_id, 'CANCEL_APPOINTMENT', f"Cancelled appointment #{appointment_id}", request.remote_addr)
        flash("Appointment cancelled successfully.", "info")

    return redirect(request.referrer or url_for('appointments.index'))


@appointments_bp.route('/<int:appointment_id>/status', methods=['POST'])
@role_required('admin', 'doctor')
def update_status(appointment_id):
    """Update appointment state (e.g. Completed, Confirmed)."""
    new_status = request.form.get('status')
    notes = request.form.get('notes')
    ok, err = update_appointment_status(appointment_id, new_status, notes)
    if not ok:
        flash(err, "danger")
    else:
        log_activity(session['user_id'], 'UPDATE_STATUS', f"Changed appointment #{appointment_id} status to {new_status}", request.remote_addr)
        flash(f"Appointment updated to '{new_status}'.", "success")

    return redirect(request.referrer or url_for('appointments.index'))
