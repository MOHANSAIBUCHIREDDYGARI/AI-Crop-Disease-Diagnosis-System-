from flask import Blueprint, request, jsonify
import sys
import os

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

chatbot_bp = Blueprint('chatbot', __name__)

# Configure Gemini API (if available)
if GEMINI_AVAILABLE and settings.GOOGLE_GEMINI_API_KEY:
    try:
        genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
    except:
        model = None
else:
    model = None

def get_chatbot_response(message: str, language: str = 'en', context: str = '') -> str:
    """
    Get chatbot response using Google Gemini or fallback
    
    Args:
        message: User message
        language: Language code
        context: Additional context about user's crops/diseases
        
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
            # Translate message to English if needed
            if language != 'en':
                message_en = translate_text(message, 'en', language)
            else:
                message_en = message
            
            # Get response from Gemini
            full_prompt = system_prompt + "\nUser: " + message_en + "\nAssistant:"
            response = model.generate_content(full_prompt)
            answer = response.text
            
            # Translate response back to user's language
            if language != 'en':
                answer = translate_text(answer, language, 'en')
            
            return answer
        except Exception as e:
            print(f"Gemini API error: {e}")
            return get_fallback_response(message, language)
    else:
        return get_fallback_response(message, language)

def get_fallback_response(message: str, language: str = 'en') -> str:
    """Enhanced fallback responses with agricultural knowledge"""
    message_lower = message.lower()
    
    # Enhanced keyword-based responses with detailed information
    responses = {
        'en': {
            'tomato_early_blight': "Early Blight in tomato shows brown spots with concentric rings. Treatment: Spray Mancozeb (2g/L) or Chlorothalonil (2ml/L) every 7-10 days. Organic: Neem oil (5ml/L). Prevention: Remove infected leaves, avoid overhead watering, maintain spacing.",
            'tomato_late_blight': "Late Blight is serious! Water-soaked lesions on leaves. Immediate treatment: Metalaxyl + Mancozeb (2.5g/L) every 5-7 days. Remove severely infected plants. Avoid evening watering. Cost: ₹300-500 per acre per spray.",
            'tomato_septoria': "Septoria Leaf Spot shows small circular spots. Treatment: Chlorothalonil (2ml/L) or Copper fungicide (3g/L) weekly. Organic: Bordeaux mixture (1%). Remove lower infected leaves.",
            'rice_blast': "Rice Blast causes diamond-shaped lesions. Treatment: Tricyclazole (0.6g/L) at tillering and booting stages. Or Carbendazim (1g/L). Prevention: Avoid excessive nitrogen. Cost: ₹400-600/acre.",
            'pesticide_general': "For specific pesticide recommendations, I need: 1) Which crop? 2) What symptoms? 3) Disease stage? Upload a crop image for accurate diagnosis and tailored pesticide suggestions with dosages.",
            'cost': "Treatment costs vary: Early stage (₹200-400/acre), Medium (₹500-800/acre), Severe (₹1000-1500/acre). Includes pesticides and labor. Use cost calculator after diagnosis for detailed breakdown.",
            'prevention': "Key prevention: 1) Crop rotation (3-4 years), 2) Disease-free seeds, 3) Proper spacing, 4) Drip irrigation, 5) Regular monitoring, 6) Remove infected plants, 7) Balanced fertilization.",
            'organic': "Organic treatments: Neem oil (5ml/L) for pests, Trichoderma for soil diseases, Bacillus thuringiensis for caterpillars, Bordeaux mixture (1%) for fungal diseases, Garlic-chili spray for aphids. Apply weekly.",
            'weather': "Weather impacts: High humidity + moderate temp (20-25°C) favors fungal diseases. Monsoon needs preventive sprays. Hot dry weather reduces fungal diseases but increases pests. Adjust based on forecasts.",
            'default': "I'm your agricultural assistant! Ask about: 🌱 Crop diseases (tomato, rice, wheat, cotton), 💊 Pesticides, 💰 Costs, 🌿 Organic solutions, 🛡️ Prevention, 🌦️ Weather advice. Upload crop image for diagnosis!"
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
    
    # Translate if needed
    if language != 'en':
        response = translate_text(response, language)
    
    return response

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
        
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get context from logged-in users OR from request body for guests
        context = ''
        
        # Check if diagnosis context is provided in request (for guest users)
        diagnosis_context = data.get('diagnosis_context')
        if diagnosis_context:
            # Guest user providing their current diagnosis
            crop = diagnosis_context.get('crop', '')
            disease = diagnosis_context.get('disease', '')
            severity = diagnosis_context.get('severity_percent', 0)
            if crop and disease:
                context = f"User's current diagnosis: {crop} with {disease} at {severity}% severity."
        elif user_id:
            # Logged-in user - get from database
            recent_diagnosis = db.execute_query(
                '''SELECT crop, disease, severity_percent FROM diagnosis_history 
                   WHERE user_id = ? ORDER BY created_at DESC LIMIT 1''',
                (user_id,)
            )
            
            if recent_diagnosis:
                d = recent_diagnosis[0]
                context = f"User's recent diagnosis: {d['crop']} with {d['disease']} at {d['severity_percent']}% severity."
        
        # Get chatbot response
        response_text = get_chatbot_response(message, language, context)
        
        # Save conversation only for logged-in users
        if user_id:
            db.execute_insert(
                '''INSERT INTO chatbot_conversations (user_id, message, response, language)
                   VALUES (?, ?, ?, ?)''',
                (user_id, message, response_text, language)
            )
        
        return jsonify({
            'message': message,
            'response': response_text,
            'language': language
        }), 200
        
    except Exception as e:
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
            '''SELECT message, response, language, created_at 
               FROM chatbot_conversations 
               WHERE user_id = ? 
               ORDER BY created_at DESC 
               LIMIT ?''',
            (user_id, limit)
        )
        
        chat_list = []
        for chat in history:
            chat_list.append({
                'message': chat['message'],
                'response': chat['response'],
                'language': chat['language'],
                'created_at': chat['created_at']
            })
        
        return jsonify({'history': chat_list}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
