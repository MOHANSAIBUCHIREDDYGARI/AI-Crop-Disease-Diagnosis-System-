from gtts import gTTS
import os
import hashlib
from typing import Optional
from config.settings import settings

def generate_voice(text: str, language: str = 'en', slow: bool = False) -> Optional[str]:
    """
    Generate voice output from text using Google Text-to-Speech
    
    Args:
        text: Text to convert to speech
        language: Language code (en, hi, te, ta, etc.)
        slow: Whether to speak slowly
        
    Returns:
        Path to generated audio file or None if failed
    """
    try:
        # Create voice output directory if it doesn't exist
        os.makedirs(settings.VOICE_OUTPUT_FOLDER, exist_ok=True)
        
        # Create unique filename based on text and language
        text_hash = hashlib.md5(f"{text}_{language}".encode()).hexdigest()
        filename = f"voice_{text_hash}.mp3"
        filepath = os.path.join(settings.VOICE_OUTPUT_FOLDER, filename)
        
        # Check if file already exists (cache)
        if os.path.exists(filepath):
            return filepath
        
        # Map language codes to gTTS supported codes
        lang_map = {
            'en': 'en',
            'hi': 'hi',
            'te': 'te',
            'ta': 'ta',
            'kn': 'kn',
            'mr': 'mr'
        }
        
        gtts_lang = lang_map.get(language, 'en')
        
        # Generate speech
        tts = gTTS(text=text, lang=gtts_lang, slow=slow)
        tts.save(filepath)
        
        return filepath
        
    except Exception as e:
        print(f"Error generating voice: {e}")
        return None

def generate_diagnosis_voice(diagnosis_result: dict, language: str = 'en') -> Optional[str]:
    """
    Generate voice output for diagnosis result
    
    Args:
        diagnosis_result: Diagnosis result dictionary
        language: Language code
        
    Returns:
        Path to generated audio file
    """
    # Build diagnosis message
    crop = diagnosis_result.get('crop_local', diagnosis_result.get('crop', ''))
    disease = diagnosis_result.get('disease_local', diagnosis_result.get('disease', ''))
    confidence = diagnosis_result.get('confidence', 0)
    severity = diagnosis_result.get('severity_percent', 0)
    stage = diagnosis_result.get('stage_local', diagnosis_result.get('stage', ''))
    
    # Create message based on language
    if language == 'en':
        if 'Healthy' in disease:
            message = f"Good news! Your {crop} plant is healthy. No disease detected. Confidence: {confidence} percent."
        else:
            message = f"Disease detected in your {crop} plant. Disease name: {disease}. Confidence: {confidence} percent. Severity: {severity} percent. Stage: {stage}."
    else:
        # For other languages, use translated text
        if 'Healthy' in disease:
            message = f"{crop} {disease}। {confidence}%"
        else:
            message = f"{crop} {disease}। {confidence}%। {severity}%। {stage}"
    
    return generate_voice(message, language)

def generate_pesticide_voice(pesticide_info: dict, language: str = 'en') -> Optional[str]:
    """
    Generate voice output for pesticide instructions
    
    Args:
        pesticide_info: Pesticide information dictionary
        language: Language code
        
    Returns:
        Path to generated audio file
    """
    name = pesticide_info.get('name', '')
    dosage = pesticide_info.get('dosage_per_acre', '')
    frequency = pesticide_info.get('frequency', '')
    warnings = pesticide_info.get('warnings', '')
    
    if language == 'en':
        message = f"Pesticide: {name}. Dosage: {dosage}. Frequency: {frequency}. Warning: {warnings}"
    else:
        message = f"{name}। {dosage}। {frequency}। {warnings}"
    
    return generate_voice(message, language)

def generate_prevention_voice(prevention_steps: str, language: str = 'en') -> Optional[str]:
    """
    Generate voice output for prevention steps
    
    Args:
        prevention_steps: Prevention steps text
        language: Language code
        
    Returns:
        Path to generated audio file
    """
    if language == 'en':
        message = f"Prevention steps: {prevention_steps}"
    else:
        message = prevention_steps
    
    return generate_voice(message, language)

def generate_cost_voice(cost_info: dict, language: str = 'en') -> Optional[str]:
    """
    Generate voice output for cost information
    
    Args:
        cost_info: Cost information dictionary
        language: Language code
        
    Returns:
        Path to generated audio file
    """
    treatment_cost = cost_info.get('treatment_cost', 0)
    prevention_cost = cost_info.get('prevention_cost', 0)
    total_cost = cost_info.get('total_cost', 0)
    land_area = cost_info.get('land_area', 0)
    
    if language == 'en':
        message = f"Cost estimate for {land_area} acres. Treatment cost: {treatment_cost} rupees. Prevention cost: {prevention_cost} rupees. Total cost: {total_cost} rupees."
    elif language == 'hi':
        message = f"{land_area} एकड़ के लिए लागत। उपचार: {treatment_cost} रुपये। रोकथाम: {prevention_cost} रुपये। कुल: {total_cost} रुपये।"
    elif language == 'te':
        message = f"{land_area} ఎకరాలకు ఖర్చు। చికిత్స: {treatment_cost} రూపాయలు। నివారణ: {prevention_cost} రూపాయలు। మొత్తం: {total_cost} రూపాయలు।"
    elif language == 'ta':
        message = f"{land_area} ஏக்கருக்கு செலவு। சிகிச்சை: {treatment_cost} ரூபாய். தடுப்பு: {prevention_cost} ரூபாய். மொத்தம்: {total_cost} ரூபாய்."
    else:
        message = f"{land_area} {treatment_cost} {prevention_cost} {total_cost}"
    
    return generate_voice(message, language)

def cleanup_old_voice_files(days: int = 7):
    """
    Clean up voice files older than specified days
    
    Args:
        days: Number of days to keep files
    """
    try:
        import time
        current_time = time.time()
        max_age = days * 24 * 60 * 60  # Convert days to seconds
        
        for filename in os.listdir(settings.VOICE_OUTPUT_FOLDER):
            filepath = os.path.join(settings.VOICE_OUTPUT_FOLDER, filename)
            if os.path.isfile(filepath):
                file_age = current_time - os.path.getmtime(filepath)
                if file_age > max_age:
                    os.remove(filepath)
                    print(f"Deleted old voice file: {filename}")
    except Exception as e:
        print(f"Error cleaning up voice files: {e}")
