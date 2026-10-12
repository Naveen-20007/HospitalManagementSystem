"""
CareSync Doctor Management & Scheduling Tests
"""

def test_doctor_listing(client, auth):
    """Test authenticated user can browse doctors directory."""
    auth.login_patient()
    response = client.get('/doctors/')
    assert response.status_code == 200
    assert b'Dr. Test Specialist' in response.data
    assert b'Cardiology' in response.data


def test_admin_create_doctor(client, auth):
    """Test administrator can create a new doctor profile."""
    auth.login_admin()
    response = client.post('/doctors/manage', data={
        'full_name': 'Dr. Marcus Vance',
        'username': 'dr.marcus',
        'doctor_code': 'DOC-999',
        'email': 'marcus@test.com',
        'specialty': 'Neurology',
        'department': 'Brain Institute',
        'qualification': 'MD, PhD',
        'consultation_fee': '750',
        'phone': '555-4321'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'created successfully' in response.data
    assert b'Dr. Marcus Vance' in response.data


def test_doctor_slot_availability_calculation(client, auth):
    """Test AJAX slot availability endpoint computes working slots."""
    auth.login_patient()
    # Query for future date
    response = client.get('/appointments/slots?doctor_id=1&date=2026-10-25')
    assert response.status_code == 200
    data = response.get_json()
    assert 'slots' in data
    assert len(data['slots']) > 0
    assert any(s['time'] == '09:00' for s in data['slots'])
