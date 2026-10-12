"""
CareSync Queue Management Blueprint
Handles patient check-in at reception, token generation,
live queue display board, and doctor consultation progression.
"""
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app.routes.auth import login_required, role_required
from app.models import (
    check_in_patient, get_live_queue, update_queue_status,
    list_appointments, list_doctors, log_activity, get_doctor_by_user_id
)

queue_bp = Blueprint('queue', __name__, url_prefix='/queue')


@queue_bp.route('/')
def display():
    """Live public display board for hospital waiting area."""
    today_str = date.today().strftime("%Y-%m-%d")
    queue_entries = get_live_queue(today_str)
    doctors = list_doctors(available_only=True)

    # Separate into currently consulting and waiting
    in_consultation = [q for q in queue_entries if q['status'] == 'In Consultation']
    waiting = [q for q in queue_entries if q['status'] == 'Waiting']
    completed = [q for q in queue_entries if q['status'] == 'Completed']

    return render_template(
        'queue/display.html',
        in_consultation=in_consultation,
        waiting=waiting,
        completed=completed,
        doctors=doctors,
        today=today_str
    )


@queue_bp.route('/manage')
@role_required('admin', 'doctor')
def manage():
    """Reception desk queue management panel."""
    today_str = date.today().strftime("%Y-%m-%d")
    role = session['role']

    if role == 'doctor':
        doc = get_doctor_by_user_id(session['user_id'])
        doc_id = doc['id'] if doc else -1
        queue_entries = get_live_queue(today_str, doctor_id=doc_id)
        # Appointments for today not yet checked in
        today_appointments = [a for a in list_appointments(doctor_id=doc_id, app_date=today_str) if a['status'] == 'Confirmed']
    else:
        # Admin can view all
        doctor_filter = request.args.get('doctor_id', type=int)
        queue_entries = get_live_queue(today_str, doctor_id=doctor_filter)
        today_appointments = [a for a in list_appointments(doctor_id=doctor_filter, app_date=today_str) if a['status'] == 'Confirmed']

    doctors = list_doctors()

    return render_template(
        'queue/manage.html',
        queue_entries=queue_entries,
        unregistered_appointments=today_appointments,
        doctors=doctors,
        today=today_str
    )


@queue_bp.route('/checkin/<int:appointment_id>', methods=['POST'])
@role_required('admin', 'doctor')
def checkin(appointment_id):
    """Reception staff checks in arriving patient, generating token number."""
    entry, err = check_in_patient(appointment_id)
    if err and not entry:
        flash(err, "danger")
    else:
        flash(f"Patient checked in successfully! Token #{entry['queue_number']}.", "success")
        log_activity(session['user_id'], 'CHECKIN_PATIENT', f"Checked in appointment #{appointment_id} -> Token #{entry['queue_number']}", request.remote_addr)

    return redirect(request.referrer or url_for('queue.manage'))


@queue_bp.route('/<int:queue_id>/status', methods=['POST'])
@role_required('admin', 'doctor')
def update_status(queue_id):
    """Advance queue token state: Waiting -> In Consultation -> Completed."""
    new_status = request.form.get('status')
    ok, err = update_queue_status(queue_id, new_status)
    if not ok:
        flash(err, "danger")
    else:
        flash(f"Queue token updated to '{new_status}'.", "info")
        log_activity(session['user_id'], 'UPDATE_QUEUE', f"Queue token #{queue_id} status changed to {new_status}", request.remote_addr)

    return redirect(request.referrer or url_for('queue.manage'))


@queue_bp.route('/api/live')
def api_live():
    """Live queue JSON feed for dynamic frontend polling."""
    today_str = date.today().strftime("%Y-%m-%d")
    doctor_id = request.args.get('doctor_id', type=int)
    entries = get_live_queue(today_str, doctor_id=doctor_id)
    return jsonify({
        'date': today_str,
        'queue': entries,
        'count': len(entries)
    })
