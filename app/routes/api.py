"""
CareSync RESTful API Blueprint
Exposes machine-readable JSON endpoints for doctors, appointments, and hospital stats.
Enforces role-based permissions and structured error payloads.
"""
from flask import Blueprint, jsonify, request, session
from app.models import (
    list_doctors, get_doctor_by_id, list_appointments,
    get_appointment_by_id, create_appointment, get_hospital_stats
)

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/doctors', methods=['GET'])
def api_get_doctors():
    """List all available doctors with specialty details."""
    specialty = request.args.get('specialty')
    search = request.args.get('search')
    doctors = list_doctors(specialty=specialty, search=search, available_only=True)
    return jsonify({
        'status': 'success',
        'count': len(doctors),
        'doctors': doctors
    }), 200


@api_bp.route('/doctors/<int:doctor_id>', methods=['GET'])
def api_get_doctor(doctor_id):
    """Retrieve details for a single doctor."""
    doc = get_doctor_by_id(doctor_id)
    if not doc:
        return jsonify({'status': 'error', 'message': 'Doctor not found'}), 404
    return jsonify({'status': 'success', 'doctor': doc}), 200


@api_bp.route('/appointments', methods=['GET'])
def api_get_appointments():
    """Retrieve authorized list of appointments."""
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Authentication required. Please sign in.'}), 401

    role = session.get('role')
    user_id = session.get('user_id')

    if role == 'patient':
        appointments = list_appointments(patient_id=user_id)
    elif role == 'doctor':
        # Find doctor id
        from app.models import get_doctor_by_user_id
        doc = get_doctor_by_user_id(user_id)
        appointments = list_appointments(doctor_id=doc['id'] if doc else -1)
    else:  # Admin
        appointments = list_appointments()

    return jsonify({
        'status': 'success',
        'count': len(appointments),
        'appointments': appointments
    }), 200


@api_bp.route('/appointments', methods=['POST'])
def api_create_appointment():
    """Create an appointment via JSON payload."""
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Authentication required. Please sign in.'}), 401

    data = request.get_json(silent=True) or {}
    doctor_id = data.get('doctor_id')
    appointment_date = data.get('appointment_date')
    time_slot = data.get('time_slot')
    reason = data.get('reason')

    if not all([doctor_id, appointment_date, time_slot, reason]):
        return jsonify({'status': 'error', 'message': 'Missing required fields (doctor_id, appointment_date, time_slot, reason)'}), 400

    patient_id = session['user_id'] if session.get('role') == 'patient' else (data.get('patient_id') or session['user_id'])

    app, err = create_appointment(patient_id, doctor_id, appointment_date, time_slot, reason)
    if err:
        return jsonify({'status': 'error', 'message': err}), 409

    return jsonify({
        'status': 'success',
        'message': 'Appointment booked successfully',
        'appointment': app
    }), 201


@api_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
def api_get_appointment(appointment_id):
    """Retrieve details for an authorized appointment."""
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Authentication required. Please sign in.'}), 401

    app = get_appointment_by_id(appointment_id)
    if not app:
        return jsonify({'status': 'error', 'message': 'Appointment not found'}), 404

    role = session.get('role')
    user_id = session.get('user_id')

    if role == 'patient' and app['patient_id'] != user_id:
        return jsonify({'status': 'error', 'message': 'Access forbidden'}), 403

    return jsonify({'status': 'success', 'appointment': app}), 200


@api_bp.route('/stats', methods=['GET'])
def api_stats():
    """Retrieve hospital statistics summary."""
    stats = get_hospital_stats()
    return jsonify({'status': 'success', 'stats': stats}), 200
