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
from services.email_service import generate_otp, send_otp_email, store_otp, verify_otp

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
            collection='users',
            mongo_query={'email': data['email']}
        )
        
        if existing_user:
            return jsonify({'error': 'An account with this email already exists. Please login instead.'}), 409
        
        # Scramble the password so it's safe even if our database is seen
        password_hash = bcrypt.hashpw(
            data['password'].encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # Save the new user to the database (email not verified yet)
        user_id = db.execute_insert(
            collection='users',
            document={
                'email': data['email'],
                'password_hash': password_hash,
                'name': data['name'],
                'phone': data.get('phone', ''),
                'farm_location': data.get('farm_location', ''),
                'farm_size': data.get('farm_size', 0),
                'preferred_language': data.get('preferred_language', 'en'),
                'is_email_verified': False,
                'created_at': datetime.datetime.utcnow()
            }
        )
        
        return jsonify({
            'message': 'User registered successfully. Please verify your email.',
            'user_id': user_id,
            'email': data['email']
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
            collection='users',
            mongo_query={'email': data['email']}
        )
        
        if not user or len(user) == 0:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        user = user[0]
        
        # Check if the password they typed matches the scrambled one in our DB
        if not bcrypt.checkpw(data['password'].encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Create a fresh token for this session (Cast to string in case user_id is passed as ObjectId)
        token = generate_token(str(user.get('_id') or user.get('id')))
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': str(user.get('_id') or user.get('id')),
                'email': user.get('email'),
                'name': user.get('name'),
                'preferred_language': user.get('preferred_language')
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
        
        from bson.errors import InvalidId
        from bson.objectid import ObjectId

        try:
            query = {'_id': ObjectId(token_data['user_id'])}
        except InvalidId:
            query = {'id': token_data['user_id']}

        # Fetch the user's details from the database
        user = db.execute_query(
            collection='users',
            mongo_query=query
        )
        
        if not user or len(user) == 0:
            return jsonify({'error': 'User not found'}), 404
            
        user = user[0]
        
        return jsonify({
            'user': {
                'id': str(user.get('_id') or user.get('id')),
                'email': user.get('email'),
                'name': user.get('name'),
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
        
        from bson.errors import InvalidId
        from bson.objectid import ObjectId

        try:
            query = {'_id': ObjectId(token_data['user_id'])}
        except InvalidId:
            query = {'id': token_data['user_id']}
            
        # Update the database with new info
        db.execute_update(
            collection='users',
            mongo_query=query,
            update={
                'name': data.get('name'),
                'phone': data.get('phone', ''),
                'farm_location': data.get('farm_location', ''),
                'farm_size': data.get('farm_size', 0),
                'updated_at': datetime.datetime.utcnow()
            }
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
        
        from bson.errors import InvalidId
        from bson.objectid import ObjectId

        try:
            query = {'_id': ObjectId(token_data['user_id'])}
        except InvalidId:
            query = {'id': token_data['user_id']}

        # Save preference to DB
        db.execute_update(
            collection='users',
            mongo_query=query,
            update={
                'preferred_language': language,
                'updated_at': datetime.datetime.utcnow()
            }
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
                    from bson.errors import InvalidId
                    from bson.objectid import ObjectId

                    try:
                        query = {'_id': ObjectId(token_data['user_id'])}
                    except InvalidId:
                        query = {'id': token_data['user_id']}
                        
                    user = db.execute_query(collection='users', mongo_query=query)
                    if user:
                        language = user[0].get('preferred_language', language)
        
        # Fetch the translations
        translations = get_translated_ui_labels(language)
        return jsonify(translations), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------------------------
# OTP: Email Verification (Registration)
# ---------------------------------------------------------------------------

@user_bp.route('/send-otp', methods=['POST'])
def send_otp():
    """Send email verification OTP to a registered (but unverified) user."""
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        # Make sure the user exists in our database
        user = db.execute_query(collection='users', mongo_query={'email': email})
        if not user:
            return jsonify({'error': 'No account found with this email'}), 404

        # Generate and store OTP
        otp = generate_otp()
        store_otp(email, otp, purpose='verify')

        # Send the email
        sent = send_otp_email(email, otp, purpose='verify')
        if not sent:
            return jsonify({'error': 'Failed to send OTP email. Check SMTP settings in .env'}), 500

        return jsonify({'message': f'OTP sent to {email}'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/verify-email-otp', methods=['POST'])
def verify_email_otp():
    """Verify the OTP for email verification after registration."""
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        otp = data.get('otp', '').strip()

        if not email or not otp:
            return jsonify({'error': 'Email and OTP are required'}), 400

        result = verify_otp(email, otp, purpose='verify')
        if not result['valid']:
            return jsonify({'error': result['error']}), 400

        # Mark the user as email-verified
        db.execute_update(
            collection='users',
            mongo_query={'email': email},
            update={'is_email_verified': True, 'updated_at': datetime.datetime.utcnow()}
        )

        # Find user to return a login token
        user = db.execute_query(collection='users', mongo_query={'email': email})
        if user:
            user = user[0]
            token = generate_token(str(user.get('_id') or user.get('id')))
            return jsonify({
                'message': 'Email verified successfully! You are now logged in.',
                'token': token,
                'user': {
                    'id': str(user.get('_id') or user.get('id')),
                    'email': user.get('email'),
                    'name': user.get('name'),
                    'preferred_language': user.get('preferred_language', 'en')
                }
            }), 200

        return jsonify({'message': 'Email verified successfully!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------------------------
# OTP: Forgot Password / Reset Password
# ---------------------------------------------------------------------------

@user_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Send a password-reset OTP to the farmer's email."""
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        # Only send OTP if the account actually exists (security: don't reveal existence)
        user = db.execute_query(collection='users', mongo_query={'email': email})
        if not user:
            # Return success anyway (prevents email enumeration attacks)
            return jsonify({'message': 'If the email is registered, an OTP will be sent.'}), 200

        otp = generate_otp()
        store_otp(email, otp, purpose='reset')
        sent = send_otp_email(email, otp, purpose='reset')

        if not sent:
            return jsonify({'error': 'Failed to send OTP email. Check SMTP settings in .env'}), 500

        return jsonify({'message': f'Password reset OTP sent to {email}'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Verify OTP and set a new password for the user."""
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        otp = data.get('otp', '').strip()
        new_password = data.get('new_password', '')

        if not email or not otp or not new_password:
            return jsonify({'error': 'Email, OTP, and new password are required'}), 400

        if len(new_password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400

        # Verify the OTP
        result = verify_otp(email, otp, purpose='reset')
        if not result['valid']:
            return jsonify({'error': result['error']}), 400

        # Hash and save the new password
        new_hash = bcrypt.hashpw(
            new_password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        db.execute_update(
            collection='users',
            mongo_query={'email': email},
            update={
                'password_hash': new_hash,
                'updated_at': datetime.datetime.utcnow()
            }
        )

        return jsonify({'message': 'Password reset successfully. Please log in with your new password.'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
