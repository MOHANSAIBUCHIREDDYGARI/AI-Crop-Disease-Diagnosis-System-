import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application configuration settings"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # Database settings
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'crop_diagnosis.db')
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    
    # ML Model settings
    MODELS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'models')
    MODEL_MAP = {
        "tomato": os.path.join(MODELS_PATH, "tomato_disease_model.h5"),
        "rice": os.path.join(MODELS_PATH, "rice_disease_model.h5"),
        "wheat": os.path.join(MODELS_PATH, "wheat_disease_model.h5"),
        "cotton": os.path.join(MODELS_PATH, "cotton_disease_model.h5")
    }
    
    CLASS_NAMES = {
        "tomato": [
            "Healthy",
            "Tomato___Bacterial_spot",
            "Tomato___Early_blight",
            "Tomato___Late_blight",
            "Tomato___Leaf_Mold",
            "Tomato___Septoria_leaf_spot",
            "Tomato___Spider_mites Two-spotted_spider_mite",
            "Tomato___Target_Spot",
            "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
            "Tomato___Tomato_mosaic_virus"
        ],
        "rice": ["Healthy", "BrownSpot", "Hispa", "LeafBlast"],
        "wheat": ["Healthy", "Brown rust", "Yellow rust", "Loose Smut"],
        "cotton": ["Healthy", "Bacterial Blight", "Curl Virus", "Leaf Hopper Jassids"]
    }
    
    # Supported languages
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'hi': 'Hindi',
        'te': 'Telugu',
        'ta': 'Tamil',
        'kn': 'Kannada',
        'mr': 'Marathi'
    }
    
    # Translation API settings (Google Translate)
    GOOGLE_TRANSLATE_API_KEY = os.getenv('GOOGLE_TRANSLATE_API_KEY', '')
    USE_FREE_TRANSLATION = os.getenv('USE_FREE_TRANSLATION', 'True') == 'True'  # Use googletrans library
    
    # Text-to-Speech settings
    TTS_SERVICE = os.getenv('TTS_SERVICE', 'gtts')  # 'gtts' or 'google_cloud'
    GOOGLE_CLOUD_TTS_API_KEY = os.getenv('GOOGLE_CLOUD_TTS_API_KEY', '')
    VOICE_OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'voice_outputs')
    
    # Chatbot settings
    CHATBOT_SERVICE = os.getenv('CHATBOT_SERVICE', 'gemini')  # 'gemini' or 'openai'
    GOOGLE_GEMINI_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # Weather API settings
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')  # OpenWeatherMap API key
    WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/weather'
    
    # JWT settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_EXPIRATION_HOURS = 24 * 7  # 7 days
    
    # Image quality thresholds
    MIN_IMAGE_QUALITY_SCORE = 0.3  # Minimum quality score (0-1)
    MIN_IMAGE_SIZE = (100, 100)  # Minimum width, height in pixels
    MAX_IMAGE_SIZE = (4000, 4000)  # Maximum width, height in pixels
    
    # Cost calculation defaults (per acre in INR)
    DEFAULT_PESTICIDE_COST_PER_LITER = 500
    DEFAULT_LABOR_COST_PER_ACRE = 1000
    DEFAULT_PREVENTION_COST_MULTIPLIER = 0.3  # 30% of treatment cost
    
    # Severity thresholds
    SEVERITY_THRESHOLDS = {
        'healthy': (0, 5),
        'early': (5, 25),
        'moderate': (25, 50),
        'severe': (50, 75),
        'critical': (75, 100)
    }
    
    @staticmethod
    def init_app():
        """Initialize application directories"""
        os.makedirs(Settings.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Settings.VOICE_OUTPUT_FOLDER, exist_ok=True)

settings = Settings()
