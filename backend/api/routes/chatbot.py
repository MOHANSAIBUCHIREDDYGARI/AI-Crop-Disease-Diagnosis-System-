from flask import Blueprint, request, jsonify
import sys
import os
import datetime
from bson.objectid import ObjectId

# Add the project directory to the python path so we can import our modules
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


import logging

# Configure Gemini AI if we have the API key
print(f"DEBUG: GEMINI_AVAILABLE = {GEMINI_AVAILABLE}")
print(f"DEBUG: API KEY = {'set' if settings.GOOGLE_GEMINI_API_KEY else 'missing'}")

if GEMINI_AVAILABLE and settings.GOOGLE_GEMINI_API_KEY:
    try:
        genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        print("DEBUG: Gemini Initialized successfully!")
    except Exception as e:
        print(f"DEBUG: Gemini init failed: {e}")
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
    
    # Tell the AI exactly how to behave - like a friendly expert farmer!
    system_prompt = f"""You are an advanced, expert agricultural AI assistant for Smart Crop Health, acting as a highly knowledgeable agronomy advisor for farmers.

**Your Primary Goal**: 
Provide highly structured, practical, and deeply actionable advice covering ALL aspects of farming, including but not limited to:
- Crop Diseases & Pests
- Soil Health & Fertilizers (NPK handling)
- Irrigation & Water Management
- Sowing, Harvesting & Crop Cycles
- Weather Strategies & Organic Alternatives

**Strict Formatting Rules Based on Query Type**:

--- SCENARIO 1: Disease, Pest, or Treatment Queries ---
If the farmer asks about treating a disease, pest, or failing crop (e.g., "treatment for tomato early blight severe stage", "bugs on my rice"), use this exact structure:

### 🔬 Diagnosis Focus
* **Crop**: [Identified Crop, e.g., Tomato]
* **Issue/Condition**: [Identified Disease/Pest]
* **Stage Analyzed**: [Identify the stage from query, e.g., Severe]

### 🩺 Step-by-Step Action Plan
[Numbered list of immediate actions. **CRITICAL**: If the user says "severe" or "advanced", step 1 MUST be an immediate chemical/drastic intervention. If "early", emphasize organic/preventative care first.]

### 🧪 Recommended Treatments (Dosage & Application)
* **[Chemical/Organic Name 1]**: [Dosage] (e.g., 2g/L of water). [Application instructions].
* **[Chemical/Organic Name 2]**: [Dosage]. [Application instructions].

### 🛡️ Future Prevention
* [Bullet list of cultural practices: crop rotation, spacing, watering, etc.]

--- SCENARIO 2: General Farming Inquiries ---
If the farmer asks about soil, fertilizers, irrigation, seeds, or general farming practices (e.g., "how much urea for maize", "best soil for grapes", "when to harvest potatoes"):

### 🌾 Agronomy Advice: [Topic Summary]

**Key Recommendations:**
1. [Actionable step or hard fact]
2. [Actionable step or hard fact]

**💡 Expert Tip**:
[One highly useful insider tip regarding their question, e.g., a specific weather condition to watch out for or a natural hack.]

---
**Current Context (If any):**
{context}

**Tone**: Professional, authoritative yet empathetic, deeply practical. Never use giant dense paragraphs. ALWAYS use the structured Markdown above based on the scenario.
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
    # Identify keywords and pick the best pre-written response
    responses = {
        'en': {
            'tomato_early_blight': "### 🔬 Diagnosis Focus\\n* **Crop**: Tomato\\n* **Condition**: Early Blight\\n\\n### 🩺 Step-by-Step Action Plan\\n1. Remove infected lower leaves immediately.\\n2. Spray Mancozeb (2g/L) or Chlorothalonil every 7-10 days.\\n3. Limit overhead watering.",
            'tomato_late_blight': "### 🔬 Diagnosis Focus\\n* **Crop**: Tomato\\n* **Condition**: Late Blight\\n\\n### 🩺 Step-by-Step Action Plan\\n1. **CRITICAL**: Immediate chemical intervention needed (Metalaxyl + Mancozeb 2.5g/L).\\n2. Destroy heavily infected plants to stop spread.\\n3. Avoid evening watering.",
            'tomato_septoria': "### 🔬 Diagnosis Focus\\n* **Crop**: Tomato\\n* **Condition**: Septoria Leaf Spot\\n\\n### 🩺 Step-by-Step Action Plan\\n1. Apply Copper fungicide (3g/L) weekly.\\n2. Remove lower leaves.",
            'rice_blast': "### 🔬 Diagnosis Focus\\n* **Crop**: Rice\\n* **Condition**: Leaf Blast\\n\\n### 🩺 Step-by-Step Action Plan\\n1. Spray Tricyclazole (0.6g/L) during tillering.\\n2. Avoid excessive nitrogen applications.",
            'potato_early_blight': "### 🔬 Diagnosis Focus\\n* **Crop**: Potato\\n* **Condition**: Early Blight\\n\\n### 🩺 Step-by-Step Action Plan\\n1. Spray Mancozeb (2g/L).\\n2. For organic, use Copper-based sprays.\\n3. Harvest only when vines are dead.",
            'potato_late_blight': "### 🔬 Diagnosis Focus\\n* **Crop**: Potato\\n* **Condition**: Late Blight (Water Soaked Spots)\\n\\n### 🩺 Step-by-Step Action Plan\\n1. **CRITICAL**: Immediate application of Cymoxanil or Metalaxyl.\\n2. Destroy infected tubers immediately.",
            'potato_wilt': "### 🔬 Diagnosis Focus\\n* **Crop**: Potato\\n* **Condition**: Bacterial Wilt\\n\\n### 🩺 Step-by-Step Action Plan\\n1. There is no chemical cure. Uproot and burn infected plants.\\n2. Practice 3-year crop rotation.",
            'maize_rust': "### 🔬 Diagnosis Focus\\n* **Crop**: Maize\\n* **Condition**: Common Rust\\n\\n### 🩺 Step-by-Step Action Plan\\n1. If severe, apply Mancozeb (2.5g/L).\\n2. Plant resistant hybrids next season.",
            'maize_gls': "### 🔬 Diagnosis Focus\\n* **Crop**: Maize\\n* **Condition**: Gray Leaf Spot\\n\\n### 🩺 Step-by-Step Action Plan\\n1. Apply Propiconazole or Azoxystrobin fungicides.\\n2. Practice crop rotation and tillage.",
            'grape_rot': "### 🔬 Diagnosis Focus\\n* **Crop**: Grape\\n* **Condition**: Black Rot\\n\\n### 🩺 Step-by-Step Action Plan\\n1. Spray Mancozeb or Myclobutanil.\\n2. Prune vines for air circulation and remove mummified berries.",
            'cotton_blight': "### 🔬 Diagnosis Focus\\n* **Crop**: Cotton\\n* **Condition**: Bacterial Blight\\n\\n### 🩺 Step-by-Step Action Plan\\n1. Spray Copper Oxychloride (3g/L) + Streptocycline (0.1g/L).\\n2. Use acid-delinted seeds next season.",
            'wheat_rust': "### 🔬 Diagnosis Focus\\n* **Crop**: Wheat\\n* **Condition**: Wheat Rust\\n\\n### 🩺 Step-by-Step Action Plan\\n1. Spray Propiconazole (1ml/L) immediately.\\n2. Ensure proper balanced NPK fertilization.",
            'pesticide_general': "### 🌾 Agronomy Advice: Pesticides\\n\\n**Key Recommendations:**\\n1. Always wear protective gear when spraying.\\n2. Apply chemicals in the early morning or late evening.\\n\\n**💡 Expert Tip**: Please provide your specific crop and symptoms so I can recommend the exact dosage!",
            'cost': "### 🌾 Agronomy Advice: Treatment Costs\\n\\n**Key Estimates:**\\n1. Early Stage Prevention: ₹200-400/acre.\\n2. Severe Chemical Intervention: ₹1000-1500/acre.\\n\\n**💡 Expert Tip**: Catching diseases early with organic sprays is heavily cost-effective compared to late-stage chemical recovery.",
            'prevention': "### 🌾 Agronomy Advice: Disease Prevention\\n\\n**Key Recommendations:**\\n1. Practice 3-4 year crop rotation.\\n2. Use drip irrigation to keep foliage dry.\\n\\n**💡 Expert Tip**: Air circulation is key. Proper plant spacing prevents 50% of fungal problems!",
            'organic': "### 🌾 Agronomy Advice: Organic Pesticides & Solutions\\n\\n**Key Recommendations:**\\n1. Neem Oil (5ml/L) is excellent for general pest control.\\n2. Bordeaux Mixture (1%) is a strong organic fungicide.\\n\\n**💡 Expert Tip**: Bacillus thuringiensis (Bt) is perfect for organic caterpillar control!",
            'weather': "### 🌾 Agronomy Advice: Weather Strategies\\n\\n**Key Recommendations:**\\n1. High Humidity (Monsoon): Apply preventive fungal sprays (e.g., Mancozeb/Copper).\\n2. Hot & Dry: Fungal risk drops, but watch for spider mites.\\n\\n**💡 Expert Tip**: Never apply pesticides right before rain to avoid chemical run-off.",
            'default': "### 🌾 Smart Crop Health Assistant\\n\\nI'm ready to help you with:\\n* **Crop Diseases**: Tomato, Potato, Rice, Maize, Grape, Wheat, Cotton.\\n* **General Advice**: Organic solutions, weather strategies, and treatment costs.\\n\\nHow can I support your farm today?"
        }
    }
    
    # Enhanced keyword matching
    # Logic to match user keywords to the right topic
    if 'tomato' in message_lower:
        if any(word in message_lower for word in ['early blight', 'brown spot', 'ring']):
            response = responses['en']['tomato_early_blight']
        elif any(word in message_lower for word in ['late blight', 'water soaked']):
            response = responses['en']['tomato_late_blight']
        elif 'septoria' in message_lower:
            response = responses['en']['tomato_septoria']
        else:
            response = responses['en']['pesticide_general']
    elif 'rice' in message_lower and ('blast' in message_lower or 'disease' in message_lower):
        response = responses['en']['rice_blast']
    elif 'potato' in message_lower:
        if any(word in message_lower for word in ['early']):
            response = responses['en']['potato_early_blight']
        elif any(word in message_lower for word in ['late', 'water soaked', 'dark spot', 'dark water']):
            response = responses['en']['potato_late_blight']
        elif any(word in message_lower for word in ['wilt', 'bacterial']):
            response = responses['en']['potato_wilt']
        else:
            response = responses['en']['pesticide_general']
    elif 'maize' in message_lower or 'corn' in message_lower:
        if 'rust' in message_lower:
            response = responses['en']['maize_rust']
        elif any(word in message_lower for word in ['gray', 'grey', 'spot']):
            response = responses['en']['maize_gls']
        else:
            response = responses['en']['pesticide_general']
    elif 'cotton' in message_lower:
        response = responses['en']['cotton_blight']
    elif 'wheat' in message_lower:
        response = responses['en']['wheat_rust']
    elif 'grape' in message_lower and 'rot' in message_lower:
        response = responses['en']['grape_rot']
    elif any(word in message_lower for word in ['cost', 'price', 'money', 'expensive', 'rupee', 'how much']):
        response = responses['en']['cost']
    elif any(word in message_lower for word in ['prevent', 'prevention', 'avoid', 'stop']):
        response = responses['en']['prevention']
    elif any(word in message_lower for word in ['organic', 'natural', 'bio', 'neem']):
        response = responses['en']['organic']
    elif any(word in message_lower for word in ['weather', 'rain', 'monsoon', 'humidity']):
        response = responses['en']['weather']
    elif any(word in message_lower for word in ['pesticide', 'spray', 'chemical', 'fungicide', 'medicine', 'cure', 'treatment']):
        response = responses['en']['pesticide_general']
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
                
                # If logged in, use their preferred language
                users_collection = db.get_collection('users')
                user = users_collection.find_one({'_id': ObjectId(user_id)})
                if user:
                    language = user.get('preferred_language', 'en')
        
        data = request.get_json()
        message = data.get('message', '').strip()
        
        
        # Or if the app explicitly tells us the language, use that
        if 'language' in data:
            language = data['language']
            
        # Context building
        context = ''
        
        
        # If the user is looking at a specific diagnosis, tell the chatbot about it
        diagnosis_context = data.get('diagnosis_context')
        if diagnosis_context:
            
            crop = diagnosis_context.get('crop', '')
            disease = diagnosis_context.get('disease', '')
            severity = diagnosis_context.get('severity_percent', 0)
            if crop and disease:
                context = f"User's current diagnosis: {crop} with {disease} at {severity}% severity."
        elif user_id:

            
            # Or fetch their latest diagnosis from history
            diagnosis_collection = db.get_collection('diagnosis_history')
            recent_diagnosis = diagnosis_collection.find({'user_id': user_id})\
                .sort('created_at', -1)\
                .limit(1)
            
            recent_list = list(recent_diagnosis)
            if recent_list:
                d = recent_list[0]
                context = f"User's recent diagnosis: {d['crop']} with {d['disease']} at {d['severity_percent']}% severity."
        
        
        # Get the answer!
        response_text = get_chatbot_response(message, language, context)
        
        
        # Save interaction history if user is logged in
        if user_id:
            db.get_collection('chatbot_conversations').insert_one({
                'user_id': user_id,
                'message': message,
                'response': response_text,
                'language': language,
                'created_at': datetime.datetime.utcnow()
            })
        
        return jsonify({
            'message': message,
            'response': response_text,
            'language': language
        }), 200
        
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
        
        
        # Fetch conversations from database, newest first
        chat_collection = db.get_collection('chatbot_conversations')
        history = chat_collection.find({'user_id': user_id})\
            .sort('created_at', -1)\
            .limit(limit)
        
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

@chatbot_bp.route('/voice', methods=['POST'])
def process_voice():
    """Receive an audio file, send to Gemini, and return the chatbot response"""
    try:
        from werkzeug.utils import secure_filename
        
        auth_header = request.headers.get('Authorization')
        user_id = None
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            token_data = verify_token(token)
            if token_data['valid']:
                user_id = token_data['user_id']
                
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
            
        file = request.files['audio']
        if file.filename == '':
            return jsonify({'error': 'Empty audio file'}), 400
            
        language = request.form.get('language', 'en')
        
        filename = secure_filename(file.filename)
        temp_path = os.path.join(settings.UPLOAD_FOLDER, f"temp_{int(datetime.datetime.utcnow().timestamp())}_{filename}")
        file.save(temp_path)
        
        try:
            if not GEMINI_AVAILABLE or not settings.GOOGLE_GEMINI_API_KEY:
                return jsonify({'error': 'AI configuration missing for voice.'}), 503
                
            # Read the file directly into memory
            with open(temp_path, "rb") as f:
                audio_data = f.read()
            
            prompt = f"Transcribe this audio precisely into text. The language is {language}. Do not answer the user's question, just return the transcribed text."
            stt_model = genai.GenerativeModel('gemini-2.5-flash')
            
            response = stt_model.generate_content([
                prompt,
                {
                    "mime_type": "audio/mp4",
                    "data": audio_data
                }
            ])
            
            transcription = response.text.strip()
            
            return jsonify({
                'transcription': transcription,
                'language': language
            }), 200
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        print(f"Voice Error: {str(e)}")
        return jsonify({'error': str(e)}), 500
