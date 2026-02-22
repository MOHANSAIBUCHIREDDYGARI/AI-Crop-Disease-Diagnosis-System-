from flask import Blueprint, request, jsonify
import bcrypt
import jwt
import datetime
import sys
import os

# Add the project root to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.db_connection import db
from config.settings import settings
from utils.validators import validate_user_registration, validate_email, validate_language
from services.language_service import get_translated_ui_labels

# Create a 'blueprint' for all user-related routes (registration, login, profile)
user_bp = Blueprint('user', __name__)

def generate_token(user_id: int) -> str:
    """Generate a secure 'Access Badge' (JWT Token) for the user"""
    # This payload is the information hidden inside the token
    payload = {
        'user_id': user_id,
        # The token expires after a set time for security
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    }
    # Seal the token with our secret key
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')

def verify_token(token: str) -> dict:
    """Check if the user's 'Access Badge' (Token) is valid"""
    try:
        # Try to decode the token using our secret key
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
        # If successful, return the user ID hidden inside
        return {'valid': True, 'user_id': payload['user_id']}
    except jwt.ExpiredSignatureError:
        # Token is too old
        return {'valid': False, 'error': 'Token expired'}
    except jwt.InvalidTokenError:
        # Token is fake or broken
        return {'valid': False, 'error': 'Invalid token'}

@user_bp.route('/register', methods=['POST'])
def register():
    """Register a new user in our system"""
    try:
        data = request.get_json()
        
        # Check if the user filled in the form correctly
        validation = validate_user_registration(data)
        if not validation['is_valid']:
            return jsonify({'error': validation['errors']}), 400
        
        # Check if this email is already taken
        existing_user = db.execute_query(
            'SELECT id FROM users WHERE email = ?',
            (data['email'],)
        )
        
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Scramble the password so it's safe even if our database is seen
        password_hash = bcrypt.hashpw(
            data['password'].encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # Save the new user to the database
        user_id = db.execute_insert(
            '''INSERT INTO users (email, password_hash, name, phone, farm_location, farm_size, preferred_language)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (
                data['email'],
                password_hash,
                data['name'],
                data.get('phone', ''),
                data.get('farm_location', ''),
                data.get('farm_size', 0),
                data.get('preferred_language', 'en')
            )
        )
        
        # Create a token immediately so they are logged in right after signing up
        token = generate_token(user_id)
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user_id,
            'token': token
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/login', methods=['POST'])
def login():
    """Log in an existing user"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        # Find the user by their email
        user = db.execute_query(
            'SELECT id, email, password_hash, name, preferred_language FROM users WHERE email = ?',
            (data['email'],)
        )
        
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        user = user[0]
        
        # Check if the password they typed matches the scrambled one in our DB
        if not bcrypt.checkpw(data['password'].encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Create a fresh token for this session
        token = generate_token(user['id'])
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'preferred_language': user['preferred_language']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get the profile details of the logged-in user"""
    try:
        # Check for the secure token in the header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        token_data = verify_token(token)
        
        if not token_data['valid']:
            return jsonify({'error': token_data['error']}), 401
        
        # Fetch the user's details from the database
        user = db.execute_query(
            '''SELECT id, email, name, phone, farm_location, farm_size, 
                      preferred_language, created_at 
               FROM users WHERE id = ?''',
            (token_data['user_id'],)
        )
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user = user[0]
        
        return jsonify({
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'phone': user['phone'],
                'farm_location': user['farm_location'],
                'farm_size': user['farm_size'],
                'preferred_language': user['preferred_language'],
                'created_at': user['created_at']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/profile', methods=['PUT'])
def update_profile():
    """Update the user's profile information"""
    try:
        # Authenticate the user
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        token_data = verify_token(token)
        
        if not token_data['valid']:
            return jsonify({'error': token_data['error']}), 401
        
        data = request.get_json()
        
        # Update the database with new info
        db.execute_update(
            '''UPDATE users 
               SET name = ?, phone = ?, farm_location = ?, farm_size = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?''',
            (
                data.get('name'),
                data.get('phone', ''),
                data.get('farm_location', ''),
                data.get('farm_size', 0),
                token_data['user_id']
            )
        )
        
        return jsonify({'message': 'Profile updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/language', methods=['PUT'])
def update_language():
    """Update the user's preferred language"""
    try:
        # Authenticate first
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        token_data = verify_token(token)
        
        if not token_data['valid']:
            return jsonify({'error': token_data['error']}), 401
        
        data = request.get_json()
        language = data.get('language', 'en')
        
        if not validate_language(language):
            return jsonify({'error': 'Unsupported language'}), 400
        
        # Save preference to DB
        db.execute_update(
            'UPDATE users SET preferred_language = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (language, token_data['user_id'])
        )
        
        return jsonify({'message': 'Language updated successfully', 'language': language}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/translations', methods=['GET'])
def get_translations():
    """Get the UI labels in the user's language"""
    try:
        language = request.args.get('lang', 'en')
        
        # If language isn't specified, try to get it from the user's profile
        if 'lang' not in request.args:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                token_data = verify_token(token)
                if token_data['valid']:
                    user = db.execute_query('SELECT preferred_language FROM users WHERE id = ?', (token_data['user_id'],))
                    if user:
                        language = user[0]['preferred_language']
        
        # Fetch the translations
        translations = get_translated_ui_labels(language)
        return jsonify(translations), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
