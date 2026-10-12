"""
CareSync Queue Management & Sequential Token Generation Tests
"""
from datetime import date
from app.models import create_appointment, get_appointment_by_id, get_live_queue


def test_patient_check_in_generates_token(client, auth, app):
    """Test patient arrival check-in generates Token #1 and updates status."""
    auth.login_admin()
    today_str = date.today().strftime("%Y-%m-%d")

    with app.app_context():
        # Create appointment for today
        appointment, _ = create_appointment(patient_id=3, doctor_id=1, appointment_date=today_str, time_slot='09:00', reason='Checkin test')
        app_id = appointment['id']

    # Admin checks in patient
    res = client.post(f'/queue/checkin/{app_id}', follow_redirects=True)
    assert res.status_code == 200
    assert b'Patient checked in successfully' in res.data
    assert b'Token #1' in res.data

    with app.app_context():
        updated = get_appointment_by_id(app_id)
        assert updated['status'] == 'Checked In'
        assert updated['queue_number'] == 1


def test_sequential_queue_numbers_per_doctor(client, auth, app):
    """Test consecutive check-ins for the same doctor increment queue tokens sequentially (1, 2)."""
    auth.login_admin()
    today_str = date.today().strftime("%Y-%m-%d")

    with app.app_context():
        # Booking 1
        app1, _ = create_appointment(patient_id=3, doctor_id=1, appointment_date=today_str, time_slot='10:00', reason='Seq 1')
        # Booking 2
        app2, _ = create_appointment(patient_id=4, doctor_id=1, appointment_date=today_str, time_slot='10:30', reason='Seq 2')

    # Check in first
    res1 = client.post(f'/queue/checkin/{app1["id"]}', follow_redirects=True)
    assert b'Token #1' in res1.data

    # Check in second
    res2 = client.post(f'/queue/checkin/{app2["id"]}', follow_redirects=True)
    assert b'Token #2' in res2.data


def test_queue_status_progression(client, auth, app):
    """Test queue token transitions: Waiting -> In Consultation -> Completed."""
    auth.login_admin()
    today_str = date.today().strftime("%Y-%m-%d")

    with app.app_context():
        app_obj, _ = create_appointment(patient_id=3, doctor_id=1, appointment_date=today_str, time_slot='12:00', reason='Consultation flow')

    # Check in
    client.post(f'/queue/checkin/{app_obj["id"]}', follow_redirects=True)

    with app.app_context():
        queue_list = get_live_queue(today_str, doctor_id=1)
        target_entry = [q for q in queue_list if q['appointment_id'] == app_obj['id']][0]
        queue_id = target_entry['id']

    # Call patient -> In Consultation
    call_res = client.post(f'/queue/{queue_id}/status', data={'status': 'In Consultation'}, follow_redirects=True)
    assert call_res.status_code == 200

    # Complete -> Completed
    comp_res = client.post(f'/queue/{queue_id}/status', data={'status': 'Completed'}, follow_redirects=True)
    assert comp_res.status_code == 200

    with app.app_context():
        app_final = get_appointment_by_id(app_obj['id'])
        assert app_final['status'] == 'Completed'


def test_live_queue_api(client):
    """Test /queue/api/live returns JSON representation of waiting board."""
    response = client.get('/queue/api/live')
    assert response.status_code == 200
    data = response.get_json()
    assert 'queue' in data
    assert 'count' in data
