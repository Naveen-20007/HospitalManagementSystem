"""
CareSync Application Startup & Basic Routing Tests
"""

def test_app_startup(app):
    """Test that application factory starts with testing config active."""
    assert app is not None
    assert app.config['TESTING'] is True
    assert app.config['APP_NAME'] == 'CareSync'


def test_root_redirect_to_login(client):
    """Test unauthenticated root request redirects to login."""
    response = client.get('/', follow_redirects=False)
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']


def test_custom_404_handler(client):
    """Test non-existent route returns HTTP 404 with custom error page."""
    response = client.get('/nonexistent-hospital-page')
    assert response.status_code == 404
    assert b'404' in response.data
    assert b'Page or Record Not Found' in response.data
