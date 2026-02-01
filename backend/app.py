from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys

# Add paths
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config.settings import settings
from database.db_connection import db

# Import blueprints
from api.routes.user import user_bp
from api.routes.diagnosis import diagnosis_bp
from api.routes.cost import cost_bp
from api.routes.chatbot import chatbot_bp
from api.routes.weather import weather_bp
from api.routes.translations import translations_bp

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = settings.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = settings.MAX_CONTENT_LENGTH

# Enable CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize app directories
settings.init_app()

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(diagnosis_bp, url_prefix='/api/diagnosis')
app.register_blueprint(cost_bp, url_prefix='/api/cost')
app.register_blueprint(chatbot_bp, url_prefix='/api/chatbot')
app.register_blueprint(weather_bp, url_prefix='/api/weather')
app.register_blueprint(translations_bp, url_prefix='/api/translations')



# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({'error': 'File too large. Maximum size is 16MB'}), 413

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'AI Crop Diagnosis API',
        'version': '1.0.0'
    }), 200

# API info endpoint
@app.route('/api', methods=['GET'])
def api_info():
    return jsonify({
        'service': 'AI Crop Diagnosis API',
        'version': '1.0.0',
        'endpoints': {
            'user': {
                'POST /api/user/register': 'Register new user',
                'POST /api/user/login': 'Login user',
                'GET /api/user/profile': 'Get user profile',
                'PUT /api/user/profile': 'Update user profile',
                'PUT /api/user/language': 'Update preferred language'
            },
            'diagnosis': {
                'POST /api/diagnosis/detect': 'Detect disease from image',
                'GET /api/diagnosis/history': 'Get diagnosis history',
                'GET /api/diagnosis/<id>': 'Get diagnosis details',
                'GET /api/diagnosis/voice/<filename>': 'Get voice file'
            },
            'cost': {
                'POST /api/cost/calculate': 'Calculate treatment costs',
                'GET /api/cost/report/<diagnosis_id>': 'Get cost report'
            },
            'chatbot': {
                'POST /api/chatbot/message': 'Send message to chatbot',
                'GET /api/chatbot/history': 'Get chat history'
            }
        },
        'supported_crops': ['tomato', 'rice', 'wheat', 'cotton'],
        'supported_languages': ['en', 'hi', 'te', 'ta', 'kn', 'mr']
    }), 200

@app.route('/')
def index():
    """Root endpoint providing system status and guidance"""
    return jsonify({
        "status": "online",
        "service": "AI Crop Diagnosis API",
        "version": "1.0.0",
        "message": "Welcome! The API is running successfully.",
        "endpoints": {
            "health": "/health",
            "api_info": "/api",
            "diagnosis": "/api/diagnosis/detect (POST)",
            "chatbot": "/api/chatbot/message (POST)"
        },
        "documentation": "Please refer to the README.md or SUCCESS_GUIDE.md in the project root."
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🌾 AI CROP DIAGNOSIS API SERVER")
    print("=" * 60)
    print(f"Server starting on http://{settings.HOST}:{settings.PORT}")
    print(f"Debug mode: {settings.DEBUG}")
    print(f"Supported crops: tomato, rice, wheat, cotton")
    print(f"Supported languages: en, hi, te, ta, kn, mr")
    print("=" * 60)
    
    app.run(
        host=settings.HOST,
        port=settings.PORT,
        debug=settings.DEBUG
    )
