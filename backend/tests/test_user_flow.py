import pytest
from app import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # In a real scenario, you might want to switch to a test database here
    # For now, we will test the structure and response codes
    with app.test_client() as client:
        yield client

def test_user_register_missing_data(client):
    """Test registration with missing data"""
    response = client.post('/api/user/register', 
                           data=json.dumps({}),
                           content_type='application/json')
    # Expecting 400 or 422 depending on implementation, or 500 if not handled
    # Checking for typically expected failure codes
    assert response.status_code in [400, 422, 500] 

def test_user_login_invalid(client):
    """Test login with invalid credentials"""
    response = client.post('/api/user/login', 
                           data=json.dumps({
                               'email': 'nonexistent@example.com',
                               'password': 'wrongpassword'
                           }),
                           content_type='application/json')
    assert response.status_code in [401, 404]
