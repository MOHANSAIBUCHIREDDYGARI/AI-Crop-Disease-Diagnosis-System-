from flask import Blueprint, request, jsonify, send_file
import os
import sys
from werkzeug.utils import secure_filename
import datetime

# Cleanly add the project root to our python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.db_connection import db
from config.settings import settings
from utils.image_quality_check import check_image_quality, check_content_validity
from utils.preprocess import preprocess_image
from utils.validators import validate_diagnosis_request
from services.language_service import translate_diagnosis_result, translate_disease_info, translate_pesticide_info, translate_text, get_translated_ui_labels
from services.voice_service import generate_diagnosis_voice
from services.pesticide_service import get_severity_based_recommendations
from services.cost_service import calculate_total_cost
from services.weather_service import get_weather_data, get_weather_based_advice
from api.routes.user import verify_token


# Ensure we can find the ML models
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'ml'))
from final_predictor import full_prediction

# Organize our diagnosis routes
diagnosis_bp = Blueprint('diagnosis', __name__)

def allowed_file(filename):
    """Check if the uploaded file has a valid extension (like .jpg or .png)"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in settings.ALLOWED_EXTENSIONS

@diagnosis_bp.route('/detect', methods=['POST'])
def detect_disease():
    """
    The main feature: Detect disease from an uploaded image!
    Users can be logged in or anonymous.
    """
    try:
        
        user_id = None
        language = 'en'  
        
        # Debugging prints to help us see what's coming in
        print(f"DEBUG: Request files: {request.files}")
        print(f"DEBUG: Request form: {request.form}")
        print(f"DEBUG: Request headers: {dict(request.headers)}")
        
        # Check if the user is logged in
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            token_data = verify_token(token)
            
            if token_data['valid']:
                user_id = token_data['user_id']
                
                # Use their preferred language if found
                user = db.execute_query('SELECT preferred_language FROM users WHERE id = ?', (user_id,))
                if user:
                    language = user[0]['preferred_language']
        
        
        # If the app explicitly sets a language (e.g., user switched it temporarily), use that
        if 'language' in request.form and request.form['language']:
            language = request.form['language']
        
        
        # Make sure they actually sent an image
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
        
        
        # Identify the crop (e.g., tomato, rice)
        crop = request.form.get('crop', '').lower()
        print(f"DEBUG: Crop value: '{crop}'")
        if not crop or crop not in ['grape', 'maize', 'potato', 'rice', 'tomato']:
            print(f"DEBUG: Invalid crop: '{crop}'")
            return jsonify({'error': 'Valid crop type required (tomato, cotton)'}), 400
        
        
        # Get location for weather-based advice (optional)
        latitude = request.form.get('latitude', type=float)
        longitude = request.form.get('longitude', type=float)
        
        
        # Save the file securely so we can process it
        filename = secure_filename(file.filename)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        user_prefix = f"{user_id}_" if user_id else "anonymous_"
        filename = f"{user_prefix}{timestamp}_{filename}"
        filepath = os.path.join(settings.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        
        # --- QUALITY CHECKS ---
        # First, is the image blurry or too dark?
        print(f"DEBUG: Checking image quality for: {filename}")
        quality_result = check_image_quality(filepath)
        print(f"DEBUG: Quality result: {quality_result}")
        
        quality_warning = None  
        
        
        if not quality_result['is_valid']:
            
            # If dimensions are totally wrong, block it
            if 'dimensions' in quality_result and quality_result['quality_score'] == 0.0:
                 if os.path.exists(filepath):
                    os.remove(filepath)
                 return jsonify({
                    'error': 'Image Rejected',
                    'message': quality_result.get('reason'),
                    'details': 'Image dimensions are invalid.'
                }), 400

            
            # For other issues like blurriness, explain why
            error_msg = quality_result.get('reason', 'Image quality too low')
            details_msg = 'Please upload a clear, focused image.'
            
            # Translate error if needed
            if language != 'en':
                try:
                    error_msg = translate_text(error_msg, language)
                    details_msg = translate_text(details_msg, language)
                except:
                    pass

            
            if os.path.exists(filepath):
                os.remove(filepath)

            return jsonify({
                'error': 'Image Rejected',
                'message': error_msg,
                'details': details_msg
            }), 400
        
        
        # Second, does the image actually look like a leaf?
        print(f"DEBUG: Checking content validity for: {filename}")
        content_result = check_content_validity(filepath)
        print(f"DEBUG: Content result: {content_result}")
        
        if not content_result['is_valid']:
            
            if os.path.exists(filepath):
                os.remove(filepath)
            
            error_msg = content_result.get('reason')
            details_msg = 'Please upload a clear image of a crop leaf.'
            
            if language != 'en':
                try:
                    error_msg = translate_text(error_msg, language)
                    details_msg = translate_text(details_msg, language)
                except:
                    pass
            
            return jsonify({
                'error': 'Image Rejected',
                'message': error_msg,
                'details': details_msg
            }), 400
        
        
        # --- AI PREDICTION ---
        print(f"DEBUG: Starting disease prediction for crop: {crop}")
        prediction_result = full_prediction(filepath, crop)
        print(f"DEBUG: Prediction result: {prediction_result}")

        
        # (Optional code block for confidence thresholds was skipped here for now)
        if False: 
            pass # Placeholder
        
        
        # --- GATHER INFORMATION ---
        # 1. Get detailed info about the disease from our database
        disease_data = {}
        try:
            disease_info = db.execute_query(
                'SELECT * FROM diseases WHERE crop = ? AND disease_name = ?',
                (crop, prediction_result['disease'])
            )
            
            if disease_info:
                disease_data = {
                    'description': disease_info[0]['description'],
                    'symptoms': disease_info[0]['symptoms'],
                    'prevention_steps': disease_info[0]['prevention_steps']
                }
                
                # Translate it
                disease_data = translate_disease_info(disease_data, language)
        except Exception as e:
            print(f"DEBUG: Error getting disease info: {e}")
            disease_data = {}
        
        
        # 2. Get pesticide recommendations based on severity
        pesticide_recommendations = {}
        try:
            pesticide_recommendations = get_severity_based_recommendations(
                prediction_result['disease'],
                prediction_result['severity_percent'],
                crop
            )
            
            
            # Translate recommendations if needed
            if language != 'en' and pesticide_recommendations:
                if 'treatment_approach' in pesticide_recommendations:
                    pesticide_recommendations['treatment_approach'] = translate_text(
                        pesticide_recommendations['treatment_approach'], language
                    )
                if 'application_note' in pesticide_recommendations:
                    pesticide_recommendations['application_note'] = translate_text(
                        pesticide_recommendations['application_note'], language
                    )
                
                new_pests = []
                for pest in pesticide_recommendations.get('recommended_pesticides', []):
                    new_pests.append(translate_pesticide_info(pest, language))
                pesticide_recommendations['recommended_pesticides'] = new_pests

        except Exception as e:
            print(f"DEBUG: Error getting pesticide recommendations: {e}")
            pesticide_recommendations = {'recommended_pesticides': []}
        
        
        # 3. Get weather advice if we have location
        weather_advice = None
        try:
            if latitude and longitude:
                weather_data = get_weather_data(latitude, longitude)
                if weather_data:
                    weather_advice = get_weather_based_advice(weather_data, prediction_result['disease'])
        except Exception as e:
            print(f"DEBUG: Error getting weather advice: {e}")
            weather_advice = None
        
        
        # --- SAVE HISTORY ---
        diagnosis_id = None
        try:
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
                
                
                # Also save the recommended pesticides for future reference
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
        except Exception as e:
            print(f"DEBUG: Error saving to history: {e}")
            diagnosis_id = None
        
        
        # Translate the prediction labels (like "Healthy" or "Early Blight")
        translated_result = translate_diagnosis_result(prediction_result, language)
        
        
        # Get UI text (buttons, labels)
        ui_labels = get_translated_ui_labels(language)
        
        
        # Generate an audio file reading out the result
        voice_file = generate_diagnosis_voice(translated_result, language)
        
        
        # --- FINAL RESPONSE ---
        response = {
            'diagnosis_id': diagnosis_id,
            'prediction': translated_result,
            'disease_info': disease_data,
            'pesticide_recommendations': pesticide_recommendations,
            'weather_advice': weather_advice,
            'voice_file': f'/api/diagnosis/voice/{os.path.basename(voice_file)}' if voice_file else None,
            'image_quality': quality_result,
            'quality_warning': quality_warning,  
            'language': language,
            'ui_translations': ui_labels
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"CRITICAL ERROR in detect_disease: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@diagnosis_bp.route('/history', methods=['GET'])
def get_history():
    """Get the user's past diagnoses (so they can track progress)"""
    try:
        
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        token_data = verify_token(token)
        
        if not token_data['valid']:
            return jsonify({'error': token_data['error']}), 401
        
        user_id = token_data['user_id']
        
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        offset = (page - 1) * per_page
        
        
        # Fetch records from the database
        history = db.execute_query(
            '''SELECT * FROM diagnosis_history 
               WHERE user_id = ? 
               ORDER BY created_at DESC 
               LIMIT ? OFFSET ?''',
            (user_id, per_page, offset)
        )
        
        
        language = 'en'
        user = db.execute_query('SELECT preferred_language FROM users WHERE id = ?', (user_id,))
        if user:
            language = user[0]['preferred_language']

        history_list = []
        for record in history:
            item = {
                'id': record['id'],
                'crop': record['crop'],
                'disease': record['disease'],
                'confidence': record['confidence'],
                'severity_percent': record['severity_percent'],
                'stage': record['stage'],
                'created_at': record['created_at']
            }
            
            
            # Translate each record so it shows up in the user's language
            if language != 'en':
                translated = translate_diagnosis_result(item, language)
                
                if 'disease_local' in translated:
                    item['disease'] = translated['disease_local']
                if 'crop_local' in translated:
                    item['crop'] = translated['crop_local']
                if 'stage_local' in translated:
                    item['stage'] = translated['stage_local']
            
            history_list.append(item)
        
        return jsonify({'history': history_list, 'page': page, 'per_page': per_page}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@diagnosis_bp.route('/<int:diagnosis_id>', methods=['GET'])
def get_diagnosis_details(diagnosis_id):
    """Get the full details of a specific diagnosis"""
    try:
        
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        token_data = verify_token(token)
        
        if not token_data['valid']:
            return jsonify({'error': token_data['error']}), 401
        
        user_id = token_data['user_id']
        
        
        diagnosis = db.execute_query(
            'SELECT * FROM diagnosis_history WHERE id = ? AND user_id = ?',
            (diagnosis_id, user_id)
        )
        
        if not diagnosis:
            return jsonify({'error': 'Diagnosis not found'}), 404
        
        diagnosis = diagnosis[0]
        
        
        # Fetch the pesticides we recommended back then
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
        
        
        # Fetch cost calculations if they were made
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
    """Serve the audio file so the app can play it"""
    try:
        filepath = os.path.join(settings.VOICE_OUTPUT_FOLDER, filename)
        if os.path.exists(filepath):
            return send_file(filepath, mimetype='audio/mpeg')
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
