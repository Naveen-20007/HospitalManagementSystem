"""
CareSync Pytest Fixture Suite
Sets up isolated temporary databases, test clients, and authenticated sessions for test runs.
"""
import os
import tempfile
import pytest
from app import create_app
from app.db import init_db, get_db
from app.models import create_user, create_doctor, set_doctor_availability


@pytest.fixture(scope='session')
def temp_db_file():
    """Create a temporary database file for the test session."""
    fd, path = tempfile.mkstemp(suffix='.db', prefix='caresync_test_')
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def app(temp_db_file):
    """Create a test application instance configured with the temporary database."""
    # Ensure fresh schema for each test function
    if os.path.exists(temp_db_file):
        os.remove(temp_db_file)

    test_app = create_app({
        'TESTING': True,
        'DATABASE': temp_db_file,
        'SECRET_KEY': 'test-secret-key-caresync-pytest',
        'WTF_CSRF_ENABLED': False
    })

    with test_app.app_context():
        init_db(temp_db_file)
        # Seed test admin
        admin_id = create_user('test_admin', 'admin@test.com', 'adminpass', 'admin', 'Test Admin')
        # Seed test doctor
        doc_user_id = create_user('test_doc', 'doc@test.com', 'docpass', 'doctor', 'Dr. Test Specialist')
        doc_id = create_doctor(doc_user_id, 'DOC-TEST', 'Cardiology', 'MD', 500.0, 'Cardio OPD')
        # Add availability Mon-Sat
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            set_doctor_availability(doc_id, day, '09:00', '17:00', 30)

        # Seed test patient
        pat_id = create_user('test_patient', 'patient@test.com', 'patpass', 'patient', 'Test Patient', '555-1234')
        # Seed second patient
        create_user('test_patient2', 'patient2@test.com', 'patpass', 'patient', 'Second Patient', '555-5678')

    yield test_app


@pytest.fixture
def client(app):
    """Return a Flask test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Return a Flask CLI test runner."""
    return app.test_cli_runner()


class AuthActions:
    """Helper class to authenticate test client sessions."""
    def __init__(self, client):
        self._client = client

    def login(self, identifier='test_patient', password='patpass'):
        return self._client.post('/auth/login', data={
            'identifier': identifier,
            'password': password
        }, follow_redirects=True)

    def login_admin(self):
        return self.login('test_admin', 'adminpass')

    def login_doctor(self):
        return self.login('test_doc', 'docpass')

    def login_patient(self):
        return self.login('test_patient', 'patpass')

    def logout(self):
        return self._client.get('/auth/logout', follow_redirects=True)


@pytest.fixture
def auth(client):
    """Return AuthActions helper for client."""
    return AuthActions(client)
