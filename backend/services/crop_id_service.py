import google.generativeai as genai
import PIL.Image as PILImage
import os
import sys

# Add project root to path for config access if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings

def log_debug(message):
    """Log to the shared debug file"""
    try:
        with open('chatbot_debug.log', 'a', encoding='utf-8') as f:
            import datetime
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{timestamp}] [CROP_ID] {message}\n")
    except:
        pass

def identify_crop_from_image(image_path):
    """
    Use Gemini AI to identify the crop from a leaf image.
    Returns: crop name (str) or None
    """
    if not settings.GOOGLE_GEMINI_API_KEY:
        log_debug("Gemini API Key missing")
        return _fallback_ml_identification(image_path)
        
    try:
        genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)
        # Using fast multimodal model 'gemma-3-27b-it'
        model = genai.GenerativeModel('models/gemma-3-27b-it')
        
        if not os.path.exists(image_path):
            log_debug(f"Image not found: {image_path}")
            return None
            
        img = PILImage.open(image_path)
        log_debug(f"Identifying crop for: {os.path.basename(image_path)}")
        
        prompt = (
            "You are an agricultural expert. Look at this leaf carefully. "
            "Determine which crop it is. Your answer MUST be one of: "
            "rice, tomato, grape, maize, potato, wheat, cotton. "
            "If you see symptoms of a disease, mention the crop first. "
            "Respond with ONLY the crop name."
        )
        
        response = model.generate_content([prompt, img])
        raw_text = response.text.strip().lower()
        log_debug(f"Gemini Raw Response: {raw_text!r}")
        
        valid_crops = ['rice', 'tomato', 'grape', 'maize', 'potato', 'wheat', 'cotton']
        for crop in valid_crops:
            if crop in raw_text:
                log_debug(f"Successfully identified crop: {crop}")
                return crop
                
        log_debug("No valid crop found in Gemini response")
        return None
    except Exception as e:
        log_debug(f"Error in identify_crop_from_image: {e}")
        return _fallback_ml_identification(image_path)

def _fallback_ml_identification(image_path):
    """Fallback to local ML models to identify the crop if Gemini fails"""
    try:
        log_debug("Falling back to local ML models for crop identification.")
        # Dynamically import to avoid circular dependencies
        ml_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ml'))
        if ml_dir not in sys.path:
            sys.path.insert(0, ml_dir)
            
        from final_predictor import MODEL_MAP, CLASS_NAMES
        from disease_classifier import predict
        
        best_crop = None
        highest_confidence = -1.0
        
        # Test the image against every crop model
        for crop, model_path in MODEL_MAP.items():
            if not os.path.exists(model_path):
                continue
                
            try:
                # The Cotton model has an invalid config dictionary that throws an exception inside InputLayer
                # Ignore crop models that are broken
                disease, confidence = predict(image_path, model_path, CLASS_NAMES[crop])
                log_debug(f"Fallback check {crop}: {disease} ({confidence:.1f}%)")
                
                # We are looking for the model that is most confident about its prediction
                if confidence > highest_confidence:
                    highest_confidence = confidence
                    best_crop = crop
            except Exception as model_err:
                log_debug(f"Error checking model {crop}: {model_err}")
                
        # If the best model is reasonably confident, use it
        if best_crop and highest_confidence > 40.0:
            log_debug(f"Fallback identified crop as {best_crop} with {highest_confidence:.1f}% confidence")
            return best_crop
        else:
            log_debug(f"Fallback could not confidently identify crop. Best: {best_crop} at {highest_confidence:.1f}%")
            return None
            
    except Exception as e:
        log_debug(f"Fallback ML error: {e}")
        import traceback
        log_debug(traceback.format_exc())
        return None
