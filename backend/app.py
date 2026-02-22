from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys

# Ensure Python can find our other files by adding the project root to the path
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Load our app settings and database connection
from config.settings import settings
from database.db_connection import db

# Bring in the different parts of our API (Blueprints)
from api.routes.user import user_bp
from api.routes.diagnosis import diagnosis_bp
from api.routes.cost import cost_bp
from api.routes.chatbot import chatbot_bp
from api.routes.weather import weather_bp
from api.routes.translations import translations_bp


# Initialize the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = settings.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = settings.MAX_CONTENT_LENGTH


# Enable CORS so our mobile app can talk to this server without issues
CORS(app, resources={r"/api/*": {"origins": "*"}})


# Start up the settings (like creating folders)
settings.init_app()


# Register the blueprints - these are like mini-apps for each feature
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(diagnosis_bp, url_prefix='/api/diagnosis')
app.register_blueprint(cost_bp, url_prefix='/api/cost')
app.register_blueprint(chatbot_bp, url_prefix='/api/chatbot')
app.register_blueprint(weather_bp, url_prefix='/api/weather')
app.register_blueprint(translations_bp, url_prefix='/api/translations')




# If a page isn't found, tell the user politely
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

# If the server breaks, admit it
@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# If the uploaded file is too big, warn them
@app.errorhandler(413)
def file_too_large(error):
    return jsonify({'error': 'File too large. Maximum size is 16MB'}), 413


# A simple health check to see if the server is running
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Smart Crop Health API',
        'version': '1.0.0'
    }), 200


# Provide information about available API endpoints
@app.route('/api', methods=['GET'])
def api_info():
    return jsonify({
        'service': 'Smart Crop Health API',
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
        'supported_crops': ['grape', 'maize', 'potato', 'rice', 'tomato'],
        'supported_languages': ['en', 'hi', 'te', 'ta', 'kn', 'mr']
    }), 200

# The root page - just a welcome message
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
    # Print some friendly startup messages
    print("=" * 60)
    print("🌾 SMART CROP HEALTH API SERVER")
    print("=" * 60)
    print(f"Server starting on http://{settings.HOST}:{settings.PORT}")
    print(f"Debug mode: {settings.DEBUG}")
    print(f"Supported crops: grape, maize, potato, rice, tomato")
    print(f"Supported languages: en, hi, te, ta, kn, mr")
    print("=" * 60)
    
    # Start the server!
    app.run(
        host=settings.HOST,
        port=settings.PORT,
        debug=settings.DEBUG
    )
