from flask import Blueprint, request, jsonify, send_file
import os
import sys
from werkzeug.utils import secure_filename
import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.db_connection import db
from config.settings import settings
from utils.image_quality_check import check_image_quality
from utils.preprocess import preprocess_image
from utils.validators import validate_diagnosis_request
from services.language_service import translate_diagnosis_result, translate_disease_info
from services.voice_service import generate_diagnosis_voice
from services.pesticide_service import get_severity_based_recommendations
from services.cost_service import calculate_total_cost
from services.weather_service import get_weather_data, get_weather_based_advice
from api.routes.user import verify_token

# Import ML prediction function
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'ml'))
from final_predictor import full_prediction

diagnosis_bp = Blueprint('diagnosis', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in settings.ALLOWED_EXTENSIONS

@diagnosis_bp.route('/detect', methods=['POST'])
def detect_disease():
    """Detect disease from uploaded image (authentication optional)"""
    try:
        # Check for authentication (optional)
        user_id = None
        language = 'en'  # Default language
        
        # DEBUG: Print request details
        print(f"DEBUG: Request files: {request.files}")
        print(f"DEBUG: Request form: {request.form}")
        print(f"DEBUG: Request headers: {dict(request.headers)}")
        
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            token_data = verify_token(token)
            
            if token_data['valid']:
                user_id = token_data['user_id']
                # Get user's preferred language
                user = db.execute_query('SELECT preferred_language FROM users WHERE id = ?', (user_id,))
                if user:
                    language = user[0]['preferred_language']
        
        # Check if image file is present
        if 'image' not in request.files:
            print("DEBUG: No 'image' key in request.files")
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            print("DEBUG: Empty filename")
            return jsonify({'error': 'No selected file'}), 400
        
        if not allowed_file(file.filename):
            print(f"DEBUG: Invalid file type: {file.filename}")
            return jsonify({'error': 'Invalid file type. Only PNG, JPG, JPEG allowed'}), 400
        
        # Get crop type
        crop = request.form.get('crop', '').lower()
        print(f"DEBUG: Crop value: '{crop}'")
        if not crop or crop not in ['tomato', 'rice', 'wheat', 'cotton']:
            print(f"DEBUG: Invalid crop: '{crop}'")
            return jsonify({'error': 'Valid crop type required (tomato, rice, wheat, cotton)'}), 400
        
        # Get optional parameters
        latitude = request.form.get('latitude', type=float)
        longitude = request.form.get('longitude', type=float)
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        user_prefix = f"{user_id}_" if user_id else "anonymous_"
        filename = f"{user_prefix}{timestamp}_{filename}"
        filepath = os.path.join(settings.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Check image quality
        print(f"DEBUG: Checking image quality for: {filename}")
        quality_result = check_image_quality(filepath)
        print(f"DEBUG: Quality result: {quality_result}")
        
        if not quality_result['is_valid']:
            print(f"DEBUG: Image rejected - {quality_result.get('reason')}")
            os.remove(filepath)  # Delete poor quality image
            return jsonify({
                'error': 'Image quality too low',
                'reason': quality_result.get('reason'),
                'quality_score': quality_result.get('quality_score'),
                'blur_score': quality_result.get('blur_score'),
                'brightness_score': quality_result.get('brightness_score')
            }), 400
        
        print(f"DEBUG: Image quality check passed!")
        
        # Perform disease detection
        print(f"DEBUG: Starting disease prediction for crop: {crop}")
        prediction_result = full_prediction(filepath, crop)
        print(f"DEBUG: Prediction result: {prediction_result}")
        
        # Get disease information from database
        disease_info = db.execute_query(
            'SELECT * FROM diseases WHERE crop = ? AND disease_name = ?',
            (crop, prediction_result['disease'])
        )
        
        disease_data = {}
        if disease_info:
            disease_data = {
                'description': disease_info[0]['description'],
                'symptoms': disease_info[0]['symptoms'],
                'prevention_steps': disease_info[0]['prevention_steps']
            }
            # Translate disease info
            disease_data = translate_disease_info(disease_data, language)
        
        # Get pesticide recommendations
        pesticide_recommendations = get_severity_based_recommendations(
            prediction_result['disease'],
            prediction_result['severity_percent'],
            crop
        )
        
        # Get weather-based advice if coordinates provided
        weather_advice = None
        if latitude and longitude:
            weather_data = get_weather_data(latitude, longitude)
            if weather_data:
                weather_advice = get_weather_based_advice(weather_data, prediction_result['disease'])
        
        # Save diagnosis to history (only if user is logged in)
        diagnosis_id = None
        if user_id:
            diagnosis_id = db.execute_insert(
                '''INSERT INTO diagnosis_history 
                   (user_id, crop, disease, confidence, severity_percent, stage, image_path, latitude, longitude)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    user_id,
                    crop,
                    prediction_result['disease'],
                    prediction_result['confidence'],
                    prediction_result['severity_percent'],
                    prediction_result['stage'],
                    filepath,
                    latitude,
                    longitude
                )
            )
            
            # Save pesticide recommendations (only if user is logged in)
            for pesticide in pesticide_recommendations.get('recommended_pesticides', [])[:3]:
                db.execute_insert(
                    '''INSERT INTO pesticide_recommendations 
                       (diagnosis_id, pesticide_name, dosage, frequency, cost_per_unit, is_organic, warnings)
                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (
                        diagnosis_id,
                        pesticide['name'],
                        pesticide['dosage_per_acre'],
                        pesticide['frequency'],
                        pesticide['cost_per_liter'],
                        pesticide['is_organic'],
                        pesticide['warnings']
                    )
                )
        
        # Translate result
        translated_result = translate_diagnosis_result(prediction_result, language)
        
        # Generate voice output
        voice_file = generate_diagnosis_voice(translated_result, language)
        
        # Prepare response
        response = {
            'diagnosis_id': diagnosis_id,
            'prediction': translated_result,
            'disease_info': disease_data,
            'pesticide_recommendations': pesticide_recommendations,
            'weather_advice': weather_advice,
            'voice_file': f'/api/diagnosis/voice/{os.path.basename(voice_file)}' if voice_file else None,
            'image_quality': quality_result,
            'language': language
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@diagnosis_bp.route('/history', methods=['GET'])
def get_history():
    """Get user's diagnosis history"""
    try:
        # Verify token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        token_data = verify_token(token)
        
        if not token_data['valid']:
            return jsonify({'error': token_data['error']}), 401
        
        user_id = token_data['user_id']
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        offset = (page - 1) * per_page
        
        # Get history
        history = db.execute_query(
            '''SELECT * FROM diagnosis_history 
               WHERE user_id = ? 
               ORDER BY created_at DESC 
               LIMIT ? OFFSET ?''',
            (user_id, per_page, offset)
        )
        
        history_list = []
        for record in history:
            history_list.append({
                'id': record['id'],
                'crop': record['crop'],
                'disease': record['disease'],
                'confidence': record['confidence'],
                'severity_percent': record['severity_percent'],
                'stage': record['stage'],
                'created_at': record['created_at']
            })
        
        return jsonify({'history': history_list, 'page': page, 'per_page': per_page}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@diagnosis_bp.route('/<int:diagnosis_id>', methods=['GET'])
def get_diagnosis_details(diagnosis_id):
    """Get detailed diagnosis information"""
    try:
        # Verify token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        token_data = verify_token(token)
        
        if not token_data['valid']:
            return jsonify({'error': token_data['error']}), 401
        
        user_id = token_data['user_id']
        
        # Get diagnosis
        diagnosis = db.execute_query(
            'SELECT * FROM diagnosis_history WHERE id = ? AND user_id = ?',
            (diagnosis_id, user_id)
        )
        
        if not diagnosis:
            return jsonify({'error': 'Diagnosis not found'}), 404
        
        diagnosis = diagnosis[0]
        
        # Get pesticide recommendations
        pesticides = db.execute_query(
            'SELECT * FROM pesticide_recommendations WHERE diagnosis_id = ?',
            (diagnosis_id,)
        )
        
        pesticide_list = []
        for p in pesticides:
            pesticide_list.append({
                'name': p['pesticide_name'],
                'dosage': p['dosage'],
                'frequency': p['frequency'],
                'cost_per_unit': p['cost_per_unit'],
                'is_organic': bool(p['is_organic']),
                'warnings': p['warnings']
            })
        
        # Get cost calculation if exists
        cost_data = db.execute_query(
            'SELECT * FROM cost_calculations WHERE diagnosis_id = ?',
            (diagnosis_id,)
        )
        
        cost_info = None
        if cost_data:
            cost_info = {
                'land_area': cost_data[0]['land_area'],
                'treatment_cost': cost_data[0]['treatment_cost'],
                'prevention_cost': cost_data[0]['prevention_cost'],
                'total_cost': cost_data[0]['total_cost']
            }
        
        response = {
            'diagnosis': {
                'id': diagnosis['id'],
                'crop': diagnosis['crop'],
                'disease': diagnosis['disease'],
                'confidence': diagnosis['confidence'],
                'severity_percent': diagnosis['severity_percent'],
                'stage': diagnosis['stage'],
                'created_at': diagnosis['created_at']
            },
            'pesticides': pesticide_list,
            'cost': cost_info
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@diagnosis_bp.route('/voice/<filename>', methods=['GET'])
def get_voice_file(filename):
    """Serve voice file"""
    try:
        filepath = os.path.join(settings.VOICE_OUTPUT_FOLDER, filename)
        if os.path.exists(filepath):
            return send_file(filepath, mimetype='audio/mpeg')
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
