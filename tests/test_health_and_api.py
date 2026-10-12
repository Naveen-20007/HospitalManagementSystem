"""
CareSync Health Probes & Operational REST API Tests
Verifies /health, /health/ready, /metrics, and API authorization controls.
"""
from datetime import date, timedelta


def test_health_endpoint(client):
    """Test liveness probe /health returns 200 and healthy JSON."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['application'] == 'CareSync'
    assert 'version' in data
    assert 'timestamp' in data


def test_readiness_endpoint(client):
    """Test readiness probe /health/ready confirms SQLite connection."""
    response = client.get('/health/ready')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ready'
    assert data['database'] == 'connected'


def test_metrics_endpoint(client):
    """Test operational metrics /metrics provides counters."""
    response = client.get('/metrics')
    assert response.status_code == 200
    data = response.get_json()
    assert 'uptime_seconds' in data
    assert data['database_status'] == 'operational'
    assert data['total_registered_users'] >= 1


def test_api_get_doctors_public(client):
    """Test GET /api/doctors returns list of doctors without login."""
    response = client.get('/api/doctors')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['count'] >= 1
    assert any(d['specialty'] == 'Cardiology' for d in data['doctors'])


def test_unauthorized_api_requests(client):
    """Test protected API endpoints reject unauthenticated access with 401."""
    # List appointments
    res1 = client.get('/api/appointments')
    assert res1.status_code == 401
    assert 'Authentication required' in res1.get_json()['message']

    # Create appointment
    res2 = client.post('/api/appointments', json={
        'doctor_id': 1,
        'appointment_date': '2026-10-20',
        'time_slot': '10:00',
        'reason': 'Checkup'
    })
    assert res2.status_code == 401


def test_authorized_api_workflow(client, auth):
    """Test authorized patient can book and query appointments via REST API."""
    auth.login_patient()
    future_date = (date.today() + timedelta(days=5)).strftime("%Y-%m-%d")

    # Book via API
    create_res = client.post('/api/appointments', json={
        'doctor_id': 1,
        'appointment_date': future_date,
        'time_slot': '11:00',
        'reason': 'REST API Test Booking'
    })
    assert create_res.status_code == 201
    app_data = create_res.get_json()['appointment']
    assert app_data['time_slot'] == '11:00'
    app_id = app_data['id']

    # Query appointments list
    list_res = client.get('/api/appointments')
    assert list_res.status_code == 200
    assert list_res.get_json()['count'] >= 1

    # Query single appointment
    get_res = client.get(f'/api/appointments/{app_id}')
    assert get_res.status_code == 200
    assert get_res.get_json()['appointment']['id'] == app_id
