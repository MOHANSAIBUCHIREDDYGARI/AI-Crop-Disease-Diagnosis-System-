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
        return None
        
    try:
        genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)
        # Using fast multimodal model 'gemini-2.5-flash'
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
        return None
