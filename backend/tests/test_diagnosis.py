import pytest
from unittest.mock import patch, MagicMock
from app import app
import io

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_disease_prediction(client):
    """
    Test the disease prediction endpoint by mocking the ML model.
    This corresponds to the "Diagnosis Detection" integration scenario in Postman.
    It simulates sending a file ('image') and a text field ('crop') as form-data.
    """
    # Mock the full_prediction function so we don't actually run the AI
    with patch('api.routes.diagnosis.full_prediction') as mock_prediction, \
         patch('api.routes.diagnosis.check_image_quality') as mock_quality, \
         patch('api.routes.diagnosis.check_content_validity') as mock_validity:
        
        # Configure the mocks
        mock_prediction.return_value = {
            'disease': 'Tomato Early Blight',
            'confidence': 95.5,
            'severity_percent': 20.0,
            'stage': 'Early',
            'disease_local': 'Tomato Early Blight (Translated)'
        }
        mock_quality.return_value = {'is_valid': True, 'quality_score': 0.9}
        mock_validity.return_value = {'is_valid': True, 'confidence': 0.95}

        # Create a fake image file in memory
        data = {
            'image': (io.BytesIO(b"fake_image_data"), 'test_leaf.jpg'),
            'crop': 'tomato'
        }

        # Send a POST request to the API
        response = client.post(
            '/api/diagnosis/detect', 
            data=data, 
            content_type='multipart/form-data'
        )

        # Check if the API responded correctly
        assert response.status_code == 200
        json_data = response.get_json()
        
        # Verify the response contains what we expect
        assert json_data['prediction']['disease'] == 'Tomato Early Blight'
        assert json_data['prediction']['confidence'] == 95.5
        
        # Ensure the AI function was actually called
        mock_prediction.assert_called_once()
