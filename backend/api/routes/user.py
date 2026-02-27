from flask import Blueprint, request, jsonify
import bcrypt
import jwt
import datetime
import sys
import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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


def send_otp_email(to_email: str, otp: str) -> bool:
    """Send an OTP code via email using SMTP"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Your Password Reset OTP - CropAI'
        msg['From'] = settings.EMAIL_FROM
        msg['To'] = to_email

        html_body = f"""
        <html><body style="font-family:Arial,sans-serif;background:#f4f4f4;padding:30px;">
          <div style="background:#fff;border-radius:12px;padding:30px;max-width:480px;margin:auto;box-shadow:0 2px 12px rgba(0,0,0,0.1);">
            <h2 style="color:#2e7d32;">🌿 CropAI Password Reset</h2>
            <p style="color:#555;">You requested a password reset. Use the OTP below:</p>
            <div style="background:#e8f5e9;border-radius:10px;padding:20px;text-align:center;margin:24px 0;">
              <span style="font-size:40px;font-weight:bold;letter-spacing:12px;color:#1b5e20;">{otp}</span>
            </div>
            <p style="color:#777;font-size:14px;">This OTP expires in <b>10 minutes</b>.</p>
            <p style="color:#aaa;font-size:12px;">If you did not request this, please ignore this email.</p>
          </div>
        </body></html>
        """
        msg.attach(MIMEText(html_body, 'html'))

        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False


@user_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Step 1: Request OTP for password reset"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        # Check user exists
        users = db.execute_query(collection='users', mongo_query={'email': email})
        if not users:
            return jsonify({'error': 'No account found with this email address. Please check the email you registered with.'}), 404

        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)

        # Upsert OTP record (delete old one first if exists)
        db.execute_update(
            collection='password_resets',
            mongo_query={'email': email},
            update={'email': email, 'otp': otp, 'expires_at': expires_at, 'verified': False},
            upsert=True
        )

        # Send the email
        sent = send_otp_email(email, otp)
        if not sent:
            return jsonify({'error': 'Failed to send OTP email. Please check your email configuration.'}), 500

        return jsonify({'message': 'OTP sent successfully to your email'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """Step 2: Verify the OTP entered by the user"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        otp = data.get('otp', '').strip()

        if not email or not otp:
            return jsonify({'error': 'Email and OTP are required'}), 400

        # Find the OTP record
        records = db.execute_query(
            collection='password_resets',
            mongo_query={'email': email, 'otp': otp}
        )

        if not records:
            return jsonify({'error': 'Invalid OTP. Please try again.'}), 400

        record = records[0]

        # Check expiry
        if datetime.datetime.utcnow() > record['expires_at']:
            return jsonify({'error': 'OTP has expired. Please request a new one.'}), 400

        # Mark as verified so password reset can proceed
        db.execute_update(
            collection='password_resets',
            mongo_query={'email': email},
            update={'verified': True}
        )

        return jsonify({'message': 'OTP verified successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Step 3: Set a new password after OTP verification"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        otp = data.get('otp', '').strip()
        new_password = data.get('new_password', '')

        if not email or not otp or not new_password:
            return jsonify({'error': 'Email, OTP, and new password are required'}), 400

        if len(new_password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400

        # Verify OTP is still valid and was verified
        records = db.execute_query(
            collection='password_resets',
            mongo_query={'email': email, 'otp': otp, 'verified': True}
        )

        if not records:
            return jsonify({'error': 'Invalid or unverified OTP. Please restart the process.'}), 400

        record = records[0]
        if datetime.datetime.utcnow() > record['expires_at']:
            return jsonify({'error': 'OTP has expired. Please request a new one.'}), 400

        # Hash the new password
        new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Update the user's password
        db.execute_update(
            collection='users',
            mongo_query={'email': email},
            update={'password_hash': new_hash, 'updated_at': datetime.datetime.utcnow()}
        )

        # Clean up OTP record
        db.execute_delete(collection='password_resets', mongo_query={'email': email})

        return jsonify({'message': 'Password reset successfully. Please log in with your new password.'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
