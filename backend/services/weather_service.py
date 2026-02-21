import requests
from typing import Optional, Dict
from config.settings import settings

def get_weather_data(latitude: float, longitude: float) -> Optional[Dict]:
    """
    Fetch current weather conditions for the user's farm location.
    We use OpenWeatherMap API for this.
    
    Args:
        latitude: GPS Latitude
        longitude: GPS Longitude
        
    Returns:
        A dictionary with temp, humidity, rain, etc.
    """
    # Stick with defaults if we don't have an API key
    if not settings.WEATHER_API_KEY:
        return None
    
    try:
        url = settings.WEATHER_API_URL
        params = {
            'lat': latitude,
            'lon': longitude,
            'appid': settings.WEATHER_API_KEY,
            'units': 'metric' # We want degrees Celsius
        }
        
        # Call the API
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        # Pick out just the info we need
        return {
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'description': data['weather'][0]['description'],
            'wind_speed': data['wind']['speed'],
            'rain': data.get('rain', {}).get('1h', 0) # Rain in the last hour
        }
    except Exception as e:
        print(f"Weather API error: {e}")
        return None

def get_weather_based_advice(weather_data: Optional[Dict], disease_name: str) -> str:
    """
    Give smart advice based on the weather.
    Example: "Don't spray now, it's about to rain!"
    """
    if not weather_data:
        return "Monitor weather conditions. Avoid spraying during rain or high winds."
    
    advice = []
    
    # 1. Check Temperature
    temp = weather_data.get('temperature', 25)
    if temp > 35:
        advice.append("⚠️ High temperature detected. Avoid spraying pesticides during peak heat (10 AM - 4 PM). Spray in early morning or evening.")
    elif temp < 15:
        advice.append("🌡️ Cool weather. Some pesticides may be less effective. Check product guidelines.")
    
    # 2. Check Humidity (Fungi love humidity!)
    humidity = weather_data.get('humidity', 50)
    if humidity > 80:
        advice.append("💧 High humidity increases fungal disease risk. Ensure good air circulation. Fungicide application may be beneficial.")
    elif humidity < 30:
        advice.append("☀️ Low humidity. Ensure adequate irrigation. Plants may be stressed.")
    
    # 3. Check Rain
    rain = weather_data.get('rain', 0)
    if rain > 0:
        advice.append("🌧️ Rain detected. Do not spray pesticides now. Wait for dry conditions (at least 2-3 hours after rain).")
    
    # 4. Check Wind
    wind_speed = weather_data.get('wind_speed', 0)
    if wind_speed > 15:
        advice.append("💨 High wind speed. Avoid spraying to prevent drift. Wait for calmer conditions.")
    
    # Specific advice for fungal diseases (blight, spot)
    if 'blight' in disease_name.lower() or 'spot' in disease_name.lower():
        if humidity > 70 or rain > 0:
            advice.append("⚠️ Weather conditions favor disease spread. Monitor closely and apply fungicides as recommended.")
    
    # If everything looks good
    if not advice:
        advice.append("✅ Weather conditions are favorable for pesticide application.")
    
    return " ".join(advice)

def should_spray_now(weather_data: Optional[Dict]) -> Dict:
    """
    A simple Yes/No check for the user: "Can I spray right now?"
    """
    if not weather_data:
        return {
            'can_spray': True,
            'reason': 'Weather data unavailable. Use your judgment.',
            'confidence': 'low'
        }
    
    
    temp = weather_data.get('temperature', 25)
    rain = weather_data.get('rain', 0)
    wind_speed = weather_data.get('wind_speed', 0)
    
    # Don't spray in rain! It washes away.
    if rain > 0:
        return {
            'can_spray': False,
            'reason': 'Raining now. Wait for dry conditions.',
            'confidence': 'high'
        }
    
    # Don't spray in wind! It blows onto other crops or people.
    if wind_speed > 15:
        return {
            'can_spray': False,
            'reason': 'Wind speed too high. Risk of pesticide drift.',
            'confidence': 'high'
        }
    
    # Don't spray in heat! It evaporates too fast and harms the plant.
    if temp > 35:
        return {
            'can_spray': False,
            'reason': 'Temperature too high. Spray in early morning or evening.',
            'confidence': 'medium'
        }
    
    
    return {
        'can_spray': True,
        'reason': 'Weather conditions are suitable for spraying.',
        'confidence': 'high'
    }
