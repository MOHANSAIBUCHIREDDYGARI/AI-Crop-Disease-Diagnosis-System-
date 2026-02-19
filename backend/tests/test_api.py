import pytest
from app import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test that the health check endpoint returns 200 and correct status"""
    response = client.get('/health')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'healthy'
    assert json_data['service'] == 'AI Crop Diagnosis API'

def test_root_endpoint(client):
    """Test that the root endpoint returns 200 and welcome message"""
    response = client.get('/')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == 'Welcome! The API is running successfully.'
    assert 'endpoints' in json_data
