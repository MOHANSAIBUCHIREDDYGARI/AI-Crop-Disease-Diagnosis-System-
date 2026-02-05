from flask import Blueprint, request, jsonify
import sys
import os
import uuid
import json
import time
from datetime import datetime

def import_uuid():
    return str(uuid.uuid4())

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.db_connection import db
from config.settings import settings
from services.language_service import translate_text
from api.routes.user import verify_token

# Try to import Gemini, but make it optional
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

# Try to import Local ML Models
try:
    # Ensure correct path for ML models
    ml_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ml')
    if ml_path not in sys.path:
        sys.path.append(ml_path)
        
    from final_predictor import full_prediction
    ML_AVAILABLE = True
    print("DEBUG: Local ML models loaded successfully")
except ImportError as e:
    ML_AVAILABLE = False
    full_prediction = None
    print(f"DEBUG: Local ML models not available: {e}")

chatbot_bp = Blueprint('chatbot', __name__)

# Configure Gemini API (if available)
if GEMINI_AVAILABLE and settings.GOOGLE_GEMINI_API_KEY:
    try:
        genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)
        # Use a multimodal model
        model = genai.GenerativeModel('gemini-2.0-flash')
    except:
        model = None
else:
    model = None


def identify_crop_from_image(image_path):
    """
    Identify if the image contains one of the supported crops.
    Returns: 'tomato', 'rice', 'wheat', 'cotton', or None
    """
    global model
    # Dynamic re-initialization to handle hot-reloaded env vars
    if not model:
        try:
            from dotenv import load_dotenv
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
            load_dotenv(env_path, override=True)
            
            api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
            if GEMINI_AVAILABLE and api_key:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.0-flash')
            print("Gemini model successfully re-initialized with new key.")
        except Exception as e:
            print(f"Model re-init failed: {e}")

    if not model:
        print("Model is still None after re-init attempt.")
        return None
        
    try:
        import PIL.Image
        img = PIL.Image.open(image_path)
        
        prompt = """
        Analyze this image. Does it contain one of the following crops: Tomato, Rice, Wheat, Cotton?
        If yes, respond with ONLY the crop name (Tomato, Rice, Wheat, or Cotton).
        If it is a plant but not one of these, or if it is not a plant, respond with "None".
        """
        
        response = model.generate_content([prompt, img])
        text = response.text.strip().lower()
        print(f"DEBUG: Raw Gemini Crop ID Response: '{text}'")
        
        if 'tomato' in text: return 'tomato'
        if 'rice' in text: return 'rice'
        if 'wheat' in text: return 'wheat'
        if 'cotton' in text: return 'cotton'
        
        return None
    except Exception as e:
        print(f"Crop identification error (Gemini): {e}")
        # Fallback to Brute Force Local Identification
        if ML_AVAILABLE:
            print("Attempting local brute-force identification...")
            supported_crops = ['tomato', 'rice', 'wheat', 'cotton']
            best_crop = None
            max_conf = 0.0
            
            for crop in supported_crops:
                try:
                    # We need to suppress printing from full_prediction to avoid clutter logs
                    # But full_prediction prints to stdout, so we just call it.
                    result = full_prediction(image_path, crop)
                    conf = result.get('confidence', 0)
                    print(f"Local check {crop}: {conf}%")
                    
                    if conf > max_conf:
                        max_conf = conf
                        best_crop = crop
                except Exception as ml_err:
                    print(f"Local check failed for {crop}: {ml_err}")
            
            # Threshold for acceptance (e.g. 50%)
            if best_crop and max_conf > 50:
                print(f"Local identification success: {best_crop} ({max_conf}%)")
                return best_crop
                
        return None

def get_chatbot_response(message: str, language: str = 'en', context: str = '', image_path: str = None) -> str:
    """
    Get chatbot response using Google Gemini or fallback
    
    Args:
        message: User message
        language: Language code
        context: Additional context about user's crops/diseases
        image_path: Path to user uploaded image or video
        
    Returns:
        Chatbot response
    """
    # Enhanced system prompt with comprehensive agricultural knowledge
    system_prompt = f"""You are an expert agricultural assistant specializing in crop disease management for Indian farmers.

**Your Expertise:** Crop Diseases (Tomato, Rice, Wheat, Cotton), Treatment Methods, Prevention Strategies, Cost-Effective Solutions, Weather-Based Advice, Organic Farming.

**Supported Crops & Common Diseases:**

**Tomato:** Early Blight (Mancozeb 2g/L), Late Blight (Metalaxyl+Mancozeb 2.5g/L), Septoria Leaf Spot (Chlorothalonil 2ml/L), Bacterial Spot (Copper fungicides), Leaf Mold, Spider Mites (Neem oil), Yellow Leaf Curl Virus, Mosaic Virus.

**Rice:** Brown Spot (Mancozeb/Propiconazole), Hispa (Chlorpyrifos/Fipronil), Leaf Blast (Tricyclazole 0.6g/L), Bacterial Blight (Copper oxychloride).

**Wheat:** Brown Rust (Propiconazole), Yellow Rust (Tebuconazole), Loose Smut (Carboxin seed treatment).

**Cotton:** Bacterial Blight (Streptocycline), Leaf Curl Virus, Leaf Hopper/Jassids (Imidacloprid).

**Treatment Guidelines:** Early Stage (0-30%): Organic treatments. Medium (30-60%): Organic+Chemical. Severe (60%+): Immediate chemical intervention.

**Organic Alternatives:** Neem Oil (5ml/L), Trichoderma, Bacillus thuringiensis, Bordeaux Mixture (1%), Garlic-Chili spray.

**Prevention:** Crop rotation, proper spacing, drip irrigation, disease-free seeds, regular monitoring, remove infected plants, mulching.

{context}

**Response Guidelines:** Keep answers practical, provide specific dosages, include organic options, mention timing, warn about safety, suggest cost-effective solutions.
"""
    
    if model and settings.GOOGLE_GEMINI_API_KEY:
        try:
            # Prepare content parts
            content_parts = [system_prompt]
            
            # Translate message to English if needed
            if language != 'en':
                message_en = translate_text(message, 'en', language)
            else:
                message_en = message
            
            content_parts.append("User: " + message_en)
            
            # Handle Media (Image or Video)
            if image_path and os.path.exists(image_path):
                file_ext = os.path.splitext(image_path)[1].lower()
                
                if file_ext in ['.jpg', '.jpeg', '.png', '.webp']:
                    import PIL.Image
                    img = PIL.Image.open(image_path)
                    content_parts.append(img)
                    content_parts.append(" Analyze this image related to agriculture/crops if present.")
                elif file_ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm']:
                    print(f"DEBUG: Uploading video {image_path} to Gemini...")
                    video_file = genai.upload_file(image_path)
                    
                    # Wait for processing
                    while video_file.state.name == "PROCESSING":
                        print("Waiting for video processing...")
                        time.sleep(1)
                        video_file = genai.get_file(video_file.name)
                        
                    if video_file.state.name == "FAILED":
                        raise ValueError("Video processing failed")
                        
                    content_parts.append(video_file)
                    content_parts.append(" Analyze this video related to agriculture/crops if present.")
            
            content_parts.append("\nAssistant:")
            
            # Get response from Gemini
            response = model.generate_content(content_parts)
            answer = response.text.strip()
            print(f"DEBUG: Raw Gemini Crop ID Response: '{answer.lower()}'")
            
            # Translate response back to user's language
            if language != 'en':
                answer = translate_text(answer, language, 'en')
            
            return answer
        except Exception as e:
            print(f"Gemini API error: {e}")
            return get_fallback_response(message, language, context)
    else:
        return get_fallback_response(message, language, context)

def get_fallback_response(message: str, language: str = 'en', context: str = '') -> str:
    """Enhanced fallback responses with agricultural knowledge"""
    message_lower = message.lower()
    
    # Enhanced keyword-based responses with detailed information
    responses = {
        'en': {
            'tomato_early_blight': "Early Blight in tomato shows brown spots with concentric rings. Treatment: Spray Mancozeb (2g/L) or Chlorothalonil (2ml/L) every 7-10 days. Organic: Neem oil (5ml/L). Prevention: Remove infected leaves, avoid overhead watering, maintain spacing.",
            'tomato_late_blight': "Late Blight is serious! Water-soaked lesions on leaves. Immediate treatment: Metalaxyl + Mancozeb (2.5g/L) every 5-7 days. Remove severely infected plants. Avoid evening watering. Cost: ₹300-500 per acre per spray.",
            'tomato_septoria': "Septoria Leaf Spot shows small circular spots. Treatment: Chlorothalonil (2ml/L) or Copper fungicide (3g/L) weekly. Organic: Bordeaux mixture (1%). Remove lower infected leaves.",
            'rice_blast': "Rice Blast causes diamond-shaped lesions. Treatment: Tricyclazole (0.6g/L) at tillering and booting stages. Or Carbendazim (1g/L). Prevention: Avoid excessive nitrogen. Cost: ₹400-600/acre.",
            'pesticide_general': "For specific pesticide recommendations, I need: 1) Which crop? 2) What symptoms? 3) Disease stage? Upload a crop image or video for accurate diagnosis and tailored pesticide suggestions with dosages.",
            'cost': "Treatment costs vary: Early stage (₹200-400/acre), Medium (₹500-800/acre), Severe (₹1000-1500/acre). Includes pesticides and labor. Use cost calculator after diagnosis for detailed breakdown.",
            'prevention': "Key prevention: 1) Crop rotation (3-4 years), 2) Disease-free seeds, 3) Proper spacing, 4) Drip irrigation, 5) Regular monitoring, 6) Remove infected plants, 7) Balanced fertilization.",
            'organic': "Organic treatments: Neem oil (5ml/L) for pests, Trichoderma for soil diseases, Bacillus thuringiensis for caterpillars, Bordeaux mixture (1%) for fungal diseases, Garlic-chili spray for aphids. Apply weekly.",
            'weather': "Weather impacts: High humidity + moderate temp (20-25°C) favors fungal diseases. Monsoon needs preventive sprays. Hot dry weather reduces fungal diseases but increases pests. Adjust based on forecasts.",
            'default': "I'm your agricultural assistant! Ask about: 🌱 Crop diseases (tomato, rice, wheat, cotton), 💊 Pesticides, 💰 Costs, 🌿 Organic solutions, 🛡️ Prevention, 🌦️ Weather advice. Upload crop image or video for diagnosis!",
            'image_received': "I received your media! Unfortunately, my advanced vision features are currently offline, but I can still help with text questions."
        }
    }
    
    # Enhanced keyword matching
    if 'tomato' in message_lower:
        if any(word in message_lower for word in ['early blight', 'brown spot', 'ring']):
            response = responses['en']['tomato_early_blight']
        elif any(word in message_lower for word in ['late blight', 'water soaked']):
            response = responses['en']['tomato_late_blight']
        elif any(word in message_lower for word in ['septoria', 'small spot']):
            response = responses['en']['tomato_septoria']
        else:
            response = responses['en']['pesticide_general']
    elif 'rice' in message_lower and 'blast' in message_lower:
        response = responses['en']['rice_blast']
    elif any(word in message_lower for word in ['pesticide', 'spray', 'chemical', 'fungicide']):
        response = responses['en']['pesticide_general']
    elif any(word in message_lower for word in ['cost', 'price', 'money', 'expensive', 'rupee']):
        response = responses['en']['cost']
    elif any(word in message_lower for word in ['prevent', 'prevention', 'avoid', 'stop']):
        response = responses['en']['prevention']
    elif any(word in message_lower for word in ['organic', 'natural', 'bio', 'neem']):
        response = responses['en']['organic']
    elif any(word in message_lower for word in ['weather', 'rain', 'monsoon', 'humidity']):
        response = responses['en']['weather']
    else:
        response = responses['en']['default']
    
    # Prioritize diagnosis context if available
    if context and ("diagnosis system detected" in context or "User's current diagnosis" in context or "IMPORTANT" in context):
         response = context + "\n\n" + response

    # Translate if needed
    if language != 'en':
        print(f"DEBUG: Translating fallback response to {language}")
        response = translate_text(response, language)
    
    return response

@chatbot_bp.route('/upload', methods=['POST'])
def upload_media():
    """Handle media upload independently"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file:
            upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads', 'chat_uploads')
            os.makedirs(upload_folder, exist_ok=True)
            
            ext = os.path.splitext(file.filename)[1]
            if not ext:
                ext = '.jpg'
                
            filename = f"chat_upload_{import_uuid()}{ext}"
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            return jsonify({'file_path': file_path, 'message': 'Upload successful'}), 200
            
    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({'error': str(e)}), 500

@chatbot_bp.route('/message', methods=['POST'])
def send_message():
    """Send message to chatbot (authentication optional)"""
    try:
        # Check for authentication (optional)
        user_id = None
        language = 'en'  # Default language
        
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
        
        # Handle both JSON and Multipart Data
        data = {}
        file_path = None
        
        if request.content_type.startswith('multipart/form-data'):
            data = request.form.to_dict()
            if 'image' in request.files:
                file = request.files['image']
                if file.filename != '':
                    # Save file
                    upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads', 'chat_uploads')
                    os.makedirs(upload_folder, exist_ok=True)
                    
                    # Get extension from filename
                    ext = os.path.splitext(file.filename)[1]
                    if not ext:
                        ext = '.jpg' # Default backup
                        
                    filename = f"chat_{user_id or 'guest'}_{import_uuid()}{ext}" 
                    file_path = os.path.join(upload_folder, filename)
                    file.save(file_path)
                    print(f"DEBUG: Saved chat media to {file_path}")
        else:
            data = request.get_json() or {}
            # Allow passing pre-uploaded file path
            if 'image_path' in data:
                file_path = data['image_path']
            
        message = data.get('message', '')
        # Allow language override from request
        if 'language' in data:
            language = data['language']
            
        # Context building
        context = ''
        diagnosis_context_str = data.get('diagnosis_context')
        if diagnosis_context_str: # If sent as JSON string in form-data
             try:
                 if isinstance(diagnosis_context_str, str):
                     diagnosis_context = json.loads(diagnosis_context_str)
                 else:
                     diagnosis_context = diagnosis_context_str
                     
                 crop = diagnosis_context.get('crop', '')
                 disease = diagnosis_context.get('disease', '')
                 severity = diagnosis_context.get('severity_percent', 0)
                 if crop and disease:
                    context = f"User's current diagnosis: {crop} with {disease} at {severity}% severity."
             except:
                 pass
        
        # 4. Auto-detect Crop & Disease from Image if Context is Missing
        if not context and file_path and os.path.exists(file_path):
            print(f"DEBUG: Attempting auto-identification for {file_path}")
            identified_crop = identify_crop_from_image(file_path)
            
            if identified_crop:
                 print(f"DEBUG: Auto-identified crop: {identified_crop}")
                 # Run full prediction
                 if ML_AVAILABLE and full_prediction:
                     try:
                        prediction_result = full_prediction(file_path, identified_crop)
                        print(f"DEBUG: Prediction result: {prediction_result}")
                        
                        # Format disease name for better translation (replace underscores)
                        disease_display = prediction_result['disease'].replace('___', ' - ').replace('_', ' ')
                        
                        context = (
                            f"IMPORTANT: The user just uploaded an image of a {identified_crop} plant. "
                            f"My diagnosis system detected: {disease_display} "
                            f"with {prediction_result['severity_percent']}% severity (Stage: {prediction_result['stage']}). "
                            f"Confidence: {prediction_result['confidence']}%. "
                            f"Please explain this diagnosis to the user and suggest treatments based on this specific result."
                        )
                     except Exception as e:
                         print(f"DEBUG: Prediction failed after identification: {e}")
            else:
                 print("DEBUG: Could not identify crop from image.")

        if not context and user_id:
             # Logged-in user - get from database
            try:
                recent_diagnosis = db.execute_query(
                    '''SELECT crop, disease, severity_percent FROM diagnosis_history 
                       WHERE user_id = ? ORDER BY created_at DESC LIMIT 1''',
                    (user_id,)
                )
                
                if recent_diagnosis:
                    d = recent_diagnosis[0]
                    context = f"User's recent diagnosis: {d['crop']} with {d['disease']} at {d['severity_percent']}% severity."
            except Exception as e:
                print(f"Error fetching context: {e}")

        # Get chatbot response (passing image_path)
        response_text = get_chatbot_response(message, language, context, file_path)
        
        # Save interaction history if user is logged in
        if user_id:
            db.execute_query(
                'INSERT INTO chat_history (user_id, user_message, bot_response, created_at) VALUES (?, ?, ?, ?)',
                (user_id, message, response_text, datetime.now())
            )
            
        return jsonify({'response': response_text})

    except Exception as e:
        print(f"Chatbot Error: {e}")
        return jsonify({'error': str(e)}), 500

@chatbot_bp.route('/history', methods=['GET'])
def get_chat_history():
    """Get chat history"""
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
        
        # Get pagination
        limit = request.args.get('limit', 50, type=int)
        
        # Get chat history
        history = db.execute_query(
            '''SELECT user_message, bot_response, created_at 
               FROM chat_history 
               WHERE user_id = ? 
               ORDER BY created_at ASC 
               LIMIT ?''',
            (user_id, limit)
        )
        
        chat_list = []
        for chat in history:
            chat_list.append({
                'id': str(uuid.uuid4()), # Generate temp ID for frontend check
                'user_message': chat['user_message'],
                'bot_response': chat['bot_response'],
                'created_at': chat['created_at'].isoformat() if isinstance(chat['created_at'], datetime) else chat['created_at']
            })
        
        return jsonify(chat_list), 200
        
    except Exception as e:
        print(f"History Error: {e}")
        return jsonify({'error': str(e)}), 500
