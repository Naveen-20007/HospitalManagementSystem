"""
CareSync Appointments Lifecycle & Conflict Tests
Verifies booking, past date validation, duplicate conflict prevention, and cancellation.
"""
from datetime import date, timedelta
from app.models import get_appointment_by_id, list_appointments


def test_appointment_creation_success(client, auth):
    """Test successful booking by patient creates appointment with unique code."""
    auth.login_patient()
    future_date = (date.today() + timedelta(days=2)).strftime("%Y-%m-%d")

    response = client.post('/appointments/book', data={
        'doctor_id': 1,
        'appointment_date': future_date,
        'time_slot': '10:00',
        'reason': 'Routine annual cardiology checkup'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Appointment booked successfully' in response.data
    assert b'CS-' in response.data  # Appointment code prefix


def test_invalid_appointment_past_date(client, auth):
    """Test backend rejects booking attempt for past dates."""
    auth.login_patient()
    past_date = (date.today() - timedelta(days=2)).strftime("%Y-%m-%d")

    response = client.post('/appointments/book', data={
        'doctor_id': 1,
        'appointment_date': past_date,
        'time_slot': '10:00',
        'reason': 'Attempted booking in past'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'cannot be booked for past dates' in response.data


def test_duplicate_booking_prevention(client, auth):
    """
    CRITICAL REQUIREMENT: Verify duplicate booking prevention.
    Booking the same doctor, date, and time slot twice must be rejected.
    """
    auth.login_patient()
    target_date = (date.today() + timedelta(days=3)).strftime("%Y-%m-%d")

    # First booking: must succeed
    res1 = client.post('/appointments/book', data={
        'doctor_id': 1,
        'appointment_date': target_date,
        'time_slot': '14:00',
        'reason': 'First legitimate reservation'
    }, follow_redirects=True)
    assert res1.status_code == 200
    assert b'Appointment booked successfully' in res1.data

    # Log in as a different patient and attempt booking the exact same doctor and slot
    auth.logout()
    auth.login('test_patient2', 'patpass')

    res2 = client.post('/appointments/book', data={
        'doctor_id': 1,
        'appointment_date': target_date,
        'time_slot': '14:00',
        'reason': 'Conflicting double booking attempt'
    }, follow_redirects=True)

    assert res2.status_code == 200
    assert b'already booked' in res2.data


def test_appointment_cancellation(client, auth, app):
    """Test patient can cancel their confirmed appointment."""
    auth.login_patient()
    target_date = (date.today() + timedelta(days=4)).strftime("%Y-%m-%d")

    client.post('/appointments/book', data={
        'doctor_id': 1,
        'appointment_date': target_date,
        'time_slot': '15:00',
        'reason': 'To be cancelled'
    }, follow_redirects=True)

    with app.app_context():
        apps = list_appointments(app_date=target_date)
        app_id = apps[0]['id']

    # Cancel appointment
    cancel_res = client.post(f'/appointments/{app_id}/cancel', follow_redirects=True)
    assert cancel_res.status_code == 200
    assert b'cancelled successfully' in cancel_res.data

    with app.app_context():
        updated = get_appointment_by_id(app_id)
        assert updated['status'] == 'Cancelled'


def test_unauthorized_cancellation_prevention(client, auth, app):
    """Test patient cannot cancel an appointment belonging to another patient."""
    auth.login_patient()
    target_date = (date.today() + timedelta(days=6)).strftime("%Y-%m-%d")

    client.post('/appointments/book', data={
        'doctor_id': 1,
        'appointment_date': target_date,
        'time_slot': '16:00',
        'reason': 'Patient 1 Booking'
    }, follow_redirects=True)

    with app.app_context():
        apps = list_appointments(app_date=target_date)
        app_id = apps[0]['id']

    # Switch to patient 2
    auth.logout()
    auth.login('test_patient2', 'patpass')

    # Try cancelling patient 1's appointment
    res = client.post(f'/appointments/{app_id}/cancel', follow_redirects=True)
    assert res.status_code == 200
    assert b'not authorized to cancel' in res.data


def test_appointment_status_transition_to_completed(client, auth, app):
    """Test doctor or administrator can mark an appointment as Completed."""
    auth.login_admin()
    target_date = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")

    client.post('/appointments/book', data={
        'doctor_id': 1,
        'appointment_date': target_date,
        'time_slot': '11:30',
        'reason': 'Consultation transition test'
    }, follow_redirects=True)

    with app.app_context():
        apps = list_appointments(app_date=target_date)
        app_id = apps[0]['id']

    # Update status to Completed
    res = client.post(f'/appointments/{app_id}/status', data={
        'status': 'Completed',
        'notes': 'Patient treated successfully'
    }, follow_redirects=True)

    assert res.status_code == 200
    assert b'Completed' in res.data
