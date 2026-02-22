import re
from typing import Optional, Dict, Any

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """Validate phone number (Indian format)"""
    
    phone = phone.replace(' ', '').replace('-', '')
    
    pattern = r'^(\+91)?[6-9]\d{9}$'
    return re.match(pattern, phone) is not None

def validate_password(password: str) -> Dict[str, Any]:
    """
    Validate password strength
    
    Returns:
        Dictionary with is_valid and message
    """
    if len(password) < 6:
        return {
            'is_valid': False,
            'message': 'Password must be at least 6 characters long'
        }
    
    if len(password) > 50:
        return {
            'is_valid': False,
            'message': 'Password must be less than 50 characters'
        }
    
    return {
        'is_valid': True,
        'message': 'Password is valid'
    }

def validate_land_area(area: float) -> Dict[str, Any]:
    """
    Validate land area input
    
    Args:
        area: Land area in acres
        
    Returns:
        Dictionary with is_valid and message
    """
    if area <= 0:
        return {
            'is_valid': False,
            'message': 'Land area must be greater than 0'
        }
    
    if area > 10000:
        return {
            'is_valid': False,
            'message': 'Land area seems too large. Please enter area in acres.'
        }
    
    return {
        'is_valid': True,
        'message': 'Land area is valid'
    }

def validate_crop_type(crop: str) -> bool:
    """Validate if crop type is supported"""
    supported_crops = ['tomato', 'rice', 'wheat', 'cotton']
    return crop.lower() in supported_crops

def validate_language(language: str) -> bool:
    """Validate if language is supported"""
    supported_languages = ['en', 'hi', 'te', 'ta', 'kn', 'mr']
    return language.lower() in supported_languages

def validate_image_file(filename: str) -> bool:
    """Validate if file is an allowed image type"""
    allowed_extensions = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def sanitize_input(text: str, max_length: int = 500) -> str:
    """
    Sanitize user input to prevent injection attacks
    
    Args:
        text: Input text
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not text:
        return ''
    
    
    text = re.sub(r'<[^>]+>', '', text)
    
    
    text = text[:max_length]
    
    
    text = text.strip()
    
    return text

def validate_coordinates(latitude: Optional[float], longitude: Optional[float]) -> bool:
    """Validate GPS coordinates"""
    if latitude is None or longitude is None:
        return True  
    
    
    if not -90 <= latitude <= 90:
        return False
    
    
    if not -180 <= longitude <= 180:
        return False
    
    return True

def validate_user_registration(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate user registration data
    
    Args:
        data: Dictionary with user registration fields
        
    Returns:
        Dictionary with is_valid and errors list
    """
    errors = []
    
    
    if 'email' not in data or not data['email']:
        errors.append('Email is required')
    elif not validate_email(data['email']):
        errors.append('Invalid email format')
    
    
    if 'password' not in data or not data['password']:
        errors.append('Password is required')
    else:
        pwd_validation = validate_password(data['password'])
        if not pwd_validation['is_valid']:
            errors.append(pwd_validation['message'])
    
    
    if 'name' not in data or not data['name']:
        errors.append('Name is required')
    elif len(data['name']) < 2:
        errors.append('Name must be at least 2 characters')
    
    
    if 'phone' in data and data['phone']:
        if not validate_phone(data['phone']):
            errors.append('Invalid phone number format')
    
    
    if 'farm_size' in data and data['farm_size']:
        try:
            area = float(data['farm_size'])
            area_validation = validate_land_area(area)
            if not area_validation['is_valid']:
                errors.append(area_validation['message'])
        except ValueError:
            errors.append('Land area must be a number')
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors
    }

def validate_diagnosis_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate diagnosis request data
    
    Args:
        data: Dictionary with diagnosis request fields
        
    Returns:
        Dictionary with is_valid and errors list
    """
    errors = []
    
    
    if 'crop' not in data or not data['crop']:
        errors.append('Crop type is required')
    elif not validate_crop_type(data['crop']):
        errors.append('Unsupported crop type. Supported: tomato, rice, wheat, cotton')
    
    
    if 'image' not in data or not data['image']:
        errors.append('Image is required')
    
    
    if 'latitude' in data or 'longitude' in data:
        lat = data.get('latitude')
        lon = data.get('longitude')
        if not validate_coordinates(lat, lon):
            errors.append('Invalid GPS coordinates')
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors
    }
