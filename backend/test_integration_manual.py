
import os
import sys


import os
from unittest.mock import MagicMock

# Setup paths
# Add root directory to path (parent of backend)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Add backend directory
sys.path.append(os.path.dirname(__file__))
# Add ml directory
sys.path.append(os.path.join(os.path.dirname(__file__), 'ml'))

from config.settings import settings
settings.init_app()

print(f"Gemini Key Present: {bool(settings.GOOGLE_GEMINI_API_KEY)}")

# MOCK GEMINI if key missing for testing purposes
if not settings.GOOGLE_GEMINI_API_KEY:
    print("MOCKING Gemini for testing...")
    mock_response = MagicMock()
    mock_response.text = "Tomato"
    
    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response
    
    # We need to inject this into api.routes.chatbot
    # We import it first, then monkeypatch
    import api.routes.chatbot
    api.routes.chatbot.model = mock_model
    from api.routes.chatbot import identify_crop_from_image
else:
    from api.routes.chatbot import identify_crop_from_image, model

# Test Logic
try:
    image_path = os.path.abspath("../sample.JPG")
    if os.path.exists(image_path):
        print(f"Testing image: {image_path}")
        crop = identify_crop_from_image(image_path)
        print(f"Identified Crop: {crop}")
        
        if crop:
            # Test ML
            # We need to ensure ML imports are working
            # chatbot imports checks if ML_AVAILABLE. 
            pass      
            
            # Now we can try/simulate the flow in send_message...
            # But let's just test full_prediction directly
            from ml.final_predictor import full_prediction
            print("Testing Prediction...")
            result = full_prediction(image_path, crop)
            print("Prediction Result:", result)
            
            # Test Recommendation
            from services.pesticide_service import get_severity_based_recommendations
            recs = get_severity_based_recommendations(result['disease'], result['severity_percent'], crop)
            print("Recommendations:", [r['name'] for r in recs.get('recommended_pesticides', [])])
            
    else:
        print(f"sample.JPG not found at {image_path}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
