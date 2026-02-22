from flask import Blueprint, request, jsonify
import bcrypt
import jwt
import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.db_connection import db
from config.settings import settings
from utils.validators import validate_user_registration, validate_email, validate_language

user_bp = Blueprint('user', __name__)

def generate_token(user_id: str) -> str:
    """Generate a secure 'Access Badge' (JWT Token) for the user"""
    # This payload is the information hidden inside the token
    payload = {
        'user_id': str(user_id), # MongoDB ObjectIds are strings in JSON
        # The token expires after a set time for security
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')

def verify_token(token: str) -> dict:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
        return {'valid': True, 'user_id': payload['user_id']}
    except jwt.ExpiredSignatureError:
        return {'valid': False, 'error': 'Token expired'}
    except jwt.InvalidTokenError:
        return {'valid': False, 'error': 'Invalid token'}

@user_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate input
        validation = validate_user_registration(data)
        if not validation['is_valid']:
            return jsonify({'error': validation['errors']}), 400
        
        users_collection = db.get_collection('users')
        
        # Check if this email is already taken
        if users_collection.find_one({'email': data['email']}):
             return jsonify({'error': 'Email already registered'}), 400
        
        # Hash password
        password_hash = bcrypt.hashpw(
            data['password'].encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # Create user document
        new_user = {
            'email': data['email'],
            'password_hash': password_hash,
            'name': data['name'],
            'phone': data.get('phone', ''),
            'farm_location': data.get('farm_location', ''),
            'farm_size': data.get('farm_size', 0),
            'preferred_language': data.get('preferred_language', 'en'),
            'created_at': datetime.datetime.utcnow(),
            'updated_at': datetime.datetime.utcnow()
        }
        
        # Save the new user to the database
        result = users_collection.insert_one(new_user)
        user_id = str(result.inserted_id)
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
    """Login user"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        users_collection = db.get_collection('users')
        
        # Find the user by their email
        user = users_collection.find_one({'email': data['email']})
        
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        

        # Check if the password they typed matches the scrambled one in our DB
        if not bcrypt.checkpw(data['password'].encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Create a fresh token for this session
        token = generate_token(str(user['_id']))
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': str(user['_id']),
                'email': user['email'],
                'name': user['name'],
                'preferred_language': user.get('preferred_language', 'en')
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

from bson.objectid import ObjectId

@user_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get user profile"""
    try:
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        token_data = verify_token(token)
        
        if not token_data['valid']:
            return jsonify({'error': token_data['error']}), 401
        
        users_collection = db.get_collection('users')
        
        # Fetch the user's details from the database
        user = users_collection.find_one({'_id': ObjectId(token_data['user_id'])})
        
        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'user': {
                'id': str(user['_id']),
                'email': user['email'],
                'name': user['name'],
                'phone': user.get('phone', ''),
                'farm_location': user.get('farm_location', ''),
                'farm_size': user.get('farm_size', 0),
                'preferred_language': user.get('preferred_language', 'en'),
                'created_at': user.get('created_at')
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/profile', methods=['PUT'])
def update_profile():
    """Update user profile"""
    try:
        # Verify token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        token_data = verify_token(token)
        
        if not token_data['valid']:
            return jsonify({'error': token_data['error']}), 401
        
        data = request.get_json()
        users_collection = db.get_collection('users')
        
        # Update the database with new info
        users_collection.update_one(
            {'_id': ObjectId(token_data['user_id'])},
            {'$set': {
                'name': data.get('name'),
                'phone': data.get('phone', ''),
                'farm_location': data.get('farm_location', ''),
                'farm_size': data.get('farm_size', 0),
                'updated_at': datetime.datetime.utcnow()
            }}
        )
        
        return jsonify({'message': 'Profile updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/language', methods=['PUT'])
def update_language():
    """Update preferred language"""
    try:
        # Verify token
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
        
        users_collection = db.get_collection('users')
        
        # Save preference to DB
        users_collection.update_one(
            {'_id': ObjectId(token_data['user_id'])},
            {'$set': {
                'preferred_language': language,
                'updated_at': datetime.datetime.utcnow()
            }}
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
                    users_collection = db.get_collection('users')
                    user = users_collection.find_one({'_id': ObjectId(token_data['user_id'])})
                    if user:
                        language = user.get('preferred_language', 'en')
        
        # Fetch the translations
        translations = get_translated_ui_labels(language)
        return jsonify(translations), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
