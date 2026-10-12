"""
CareSync Authentication & RBAC Authorization Tests
Verifies registration, password security, session flow, and role-based route guards.
"""

def test_user_registration(client):
    """Test valid patient registration creates user account."""
    response = client.post('/auth/register', data={
        'full_name': 'New Patient',
        'username': 'newpatient',
        'email': 'newpatient@example.com',
        'phone': '555-9999',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Registration successful' in response.data


def test_registration_duplicate_username(client):
    """Test registration fails when username already taken."""
    response = client.post('/auth/register', data={
        'full_name': 'Duplicate User',
        'username': 'test_patient',  # Already in fixture
        'email': 'unique@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Username already exists' in response.data


def test_login_valid_credentials(client, auth):
    """Test logging in with valid credentials redirects to user dashboard."""
    response = auth.login_patient()
    assert response.status_code == 200
    assert b'My Health Portal' in response.data or b'Welcome back' in response.data


def test_login_invalid_credentials(client, auth):
    """Test login fails with incorrect password."""
    response = auth.login('test_patient', 'wrongpassword')
    assert response.status_code == 200
    assert b'Invalid credentials' in response.data


def test_logout(client, auth):
    """Test logout clears session and redirects to login."""
    auth.login_patient()
    response = auth.logout()
    assert response.status_code == 200
    assert b'successfully signed out' in response.data


def test_role_based_access_control(client, auth):
    """Test patient cannot access admin-only routes and gets 403 Forbidden."""
    auth.login_patient()
    # Try accessing admin dashboard
    res_admin_dash = client.get('/dashboard/admin')
    assert res_admin_dash.status_code == 403
    assert b'Access Denied' in res_admin_dash.data

    # Try accessing doctor management
    res_doc_mgmt = client.get('/doctors/manage')
    assert res_doc_mgmt.status_code == 403

    # Try accessing reports
    res_reports = client.get('/reports/')
    assert res_reports.status_code == 403
