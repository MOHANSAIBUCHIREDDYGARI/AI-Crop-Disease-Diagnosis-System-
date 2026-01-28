import requests
from typing import Optional, Dict
from config.settings import settings

def get_weather_data(latitude: float, longitude: float) -> Optional[Dict]:
    """
    Get weather data for given coordinates
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        
    Returns:
        Weather data dictionary or None
    """
    if not settings.WEATHER_API_KEY:
        return None
    
    try:
        url = settings.WEATHER_API_URL
        params = {
            'lat': latitude,
            'lon': longitude,
            'appid': settings.WEATHER_API_KEY,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'description': data['weather'][0]['description'],
            'wind_speed': data['wind']['speed'],
            'rain': data.get('rain', {}).get('1h', 0)
        }
    except Exception as e:
        print(f"Weather API error: {e}")
        return None

def get_weather_based_advice(weather_data: Optional[Dict], disease_name: str) -> str:
    """
    Get weather-aware prevention and treatment advice
    
    Args:
        weather_data: Weather information
        disease_name: Name of the disease
        
    Returns:
        Weather-based advice string
    """
    if not weather_data:
        return "Monitor weather conditions. Avoid spraying during rain or high winds."
    
    advice = []
    
    # Temperature advice
    temp = weather_data.get('temperature', 25)
    if temp > 35:
        advice.append("⚠️ High temperature detected. Avoid spraying pesticides during peak heat (10 AM - 4 PM). Spray in early morning or evening.")
    elif temp < 15:
        advice.append("🌡️ Cool weather. Some pesticides may be less effective. Check product guidelines.")
    
    # Humidity advice
    humidity = weather_data.get('humidity', 50)
    if humidity > 80:
        advice.append("💧 High humidity increases fungal disease risk. Ensure good air circulation. Fungicide application may be beneficial.")
    elif humidity < 30:
        advice.append("☀️ Low humidity. Ensure adequate irrigation. Plants may be stressed.")
    
    # Rain advice
    rain = weather_data.get('rain', 0)
    if rain > 0:
        advice.append("🌧️ Rain detected. Do not spray pesticides now. Wait for dry conditions (at least 2-3 hours after rain).")
    
    # Wind advice
    wind_speed = weather_data.get('wind_speed', 0)
    if wind_speed > 15:
        advice.append("💨 High wind speed. Avoid spraying to prevent drift. Wait for calmer conditions.")
    
    # Disease-specific advice
    if 'blight' in disease_name.lower() or 'spot' in disease_name.lower():
        if humidity > 70 or rain > 0:
            advice.append("⚠️ Weather conditions favor disease spread. Monitor closely and apply fungicides as recommended.")
    
    if not advice:
        advice.append("✅ Weather conditions are favorable for pesticide application.")
    
    return " ".join(advice)

def should_spray_now(weather_data: Optional[Dict]) -> Dict:
    """
    Determine if it's safe to spray pesticides now
    
    Args:
        weather_data: Weather information
        
    Returns:
        Dictionary with recommendation
    """
    if not weather_data:
        return {
            'can_spray': True,
            'reason': 'Weather data unavailable. Use your judgment.',
            'confidence': 'low'
        }
    
    # Check conditions
    temp = weather_data.get('temperature', 25)
    rain = weather_data.get('rain', 0)
    wind_speed = weather_data.get('wind_speed', 0)
    
    # Rain check
    if rain > 0:
        return {
            'can_spray': False,
            'reason': 'Raining now. Wait for dry conditions.',
            'confidence': 'high'
        }
    
    # Wind check
    if wind_speed > 15:
        return {
            'can_spray': False,
            'reason': 'Wind speed too high. Risk of pesticide drift.',
            'confidence': 'high'
        }
    
    # Temperature check
    if temp > 35:
        return {
            'can_spray': False,
            'reason': 'Temperature too high. Spray in early morning or evening.',
            'confidence': 'medium'
        }
    
    # All clear
    return {
        'can_spray': True,
        'reason': 'Weather conditions are suitable for spraying.',
        'confidence': 'high'
    }
