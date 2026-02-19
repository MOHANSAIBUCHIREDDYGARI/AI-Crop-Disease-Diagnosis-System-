from flask import Blueprint, request, jsonify
from services.weather_service import get_weather_data

# Create a Blueprint for weather-related routes
weather_bp = Blueprint('weather', __name__)

@weather_bp.route('', methods=['GET'])
def get_weather():
    """
    Get weather data for given coordinates.
    
    Expected Query Parameters:
    - latitude (float): The latitude of the location.
    - longitude (float): The longitude of the location.
    
    Returns:
    - JSON object containing weather details (temperature, humidity, description, etc.).
    - 400 Error if coordinates are missing.
    - 500 Error if an unexpected exception occurs.
    """
    try:
        # Retrieve latitude and longitude from request parameters
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        
        # Validate that both coordinates are provided
        if not latitude or not longitude:
            return jsonify({'error': 'Latitude and longitude required'}), 400
        
        # Fetch weather data using the service layer
        weather_data = get_weather_data(latitude, longitude)
        
        # If external API fails or no API key is set, return mock data for demonstration purposes
        if not weather_data:
            return jsonify({
                'temperature': 28,
                'humidity': 60,
                'description': 'clear sky',
                'wind_speed': 5,
                'rain': 0,
                'location': 'Your Location'
            }), 200
        
        # Add a generic location name if not present in the data
        weather_data['location'] = 'Your Location'
        
        # Return the weather data as a JSON response
        return jsonify(weather_data), 200
        
    except Exception as e:
        # Handle any unexpected errors during the process
        return jsonify({'error': str(e)}), 500
