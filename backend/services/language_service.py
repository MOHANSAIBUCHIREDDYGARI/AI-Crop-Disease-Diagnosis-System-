import json
import os
from typing import Dict
from deep_translator import GoogleTranslator

# Cache for translations to reduce API calls
# A simple memory to store words we've already translated so we don't ask Google again
translation_cache = {}


TRANSLATIONS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'database', 'seed', 'translations.json'
)

def log_debug(message):
    try:
        # Import here to avoid circular dependency if chatbot imports language_service
        with open('chatbot_debug.log', 'a', encoding='utf-8') as f:
            import datetime
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{timestamp}] [TRANS] {message}\n")
    except:
        pass

def translate_text(text: str, target_language: str = 'en', source_language: str = 'en') -> str:
    """
    Translate text to target language using Google Translate (deep-translator)
    """
    
    # If no change needed, just return the text
    if target_language == source_language or target_language == 'en':
        return text
    
    log_debug(f"Translating to {target_language}: {text[:50]}...")
    
    
    # Check our memory cache first
    cache_key = f"{text}_{source_language}_{target_language}"
    if cache_key in translation_cache:
        return translation_cache[cache_key]
    
    try:
        translator = GoogleTranslator(source=source_language, target=target_language)
        translated_text = translator.translate(text)
        
        if not translated_text:
             print(f"DEBUG: Translation returned empty for '{text}' to {target_language}")
             return text

        # Remember it for next time
        translation_cache[cache_key] = translated_text
        return translated_text
    except Exception as e:
        print(f"Translation error: {e}")
        # If it fails, at least give back the original text
        return text

def translate_batch(texts, target_language):
    """
    Translate a batch of texts using parallel processing.
    texts: dict of {key: text} where key is the ID and text is the content to translate
    target_language: language code (e.g., 'es', 'hi')
    """
    if not texts or target_language == 'en':
        return texts

    results = {}
    
    try:
        keys = list(texts.keys())
        values = list(texts.values())
        
        # deep-translator handles batch translation efficiently
        translator = GoogleTranslator(source='en', target=target_language)
        
        # Chunking to avoid timeouts or API limits with large batches
        BATCH_SIZE = 50 
        translations = []
        
        print(f"DEBUG: Starting translation of {len(values)} items in batches of {BATCH_SIZE}...")
        
        for i in range(0, len(values), BATCH_SIZE):
            chunk = values[i:i + BATCH_SIZE]
            print(f"DEBUG: Processing chunk {i//BATCH_SIZE + 1}/{(len(values)-1)//BATCH_SIZE + 1}...")
            try:
                # Translate chunk
                chunk_results = translator.translate_batch(chunk)
                translations.extend(chunk_results)
            except Exception as chunk_error:
                print(f"DEBUG: Chunk failed: {chunk_error}")
                # Fallback: append original values for this failed chunk
                translations.extend(chunk)
        
        print(f"DEBUG: translate_batch return type: {type(translations)}")
        if translations:
            print(f"DEBUG: First translated item: '{translations[0]}'")
            print(f"DEBUG: Total items translated: {len(translations)}")
        else:
            print("DEBUG: translate_batch returned empty/None")

        for i, key in enumerate(keys):
            # Fallback if something went wrong in matching indices
            if i < len(translations):
                translated_text = translations[i]
                results[key] = translated_text
                
                # Cache it
                cache_key = f"{values[i]}_en_{target_language}"
                translation_cache[cache_key] = translated_text
            else:
                results[key] = values[i]
            
    except Exception as e:
        print(f"Batch translation error: {e}") 
        # Fallback to individual translation if batch fails
        for key, text in texts.items():
            results[key] = translate_text(text, target_language)
            
    return results

def translate_diagnosis_result(result, target_language):
    """
    Translate the final diagnosis report (Disease Name, Crop Name, Stage).
    """
    if target_language == 'en':
        return result
    
    translated = result.copy()
    
    
    # Translate Disease Name (make it look nice too)
    if 'disease' in result:
        translated['disease_local'] = translate_text(
            result['disease'].replace('___', ' - ').replace('_', ' '),
            target_language
        )
    
    
    # Translate Stage (Early, Moderate, Severe)
    if 'stage' in result:
        translated['stage_local'] = translate_text(result['stage'], target_language)
    
    
    # Translate Crop Name (using our own dictionary for better accuracy)
    if 'crop' in result:
        # Pre-defined names are often better than machine translation for simple words
        crop_names = {
            'tomato': {'hi': 'टमाटर', 'te': 'టమాటా', 'ta': 'தக்காளி', 'kn': 'ಟೊಮೇಟೊ', 'mr': 'टोमॅटो'},
            'rice': {'hi': 'चावल', 'te': 'వరి', 'ta': 'அரிசி', 'kn': 'ಅಕ್ಕಿ', 'mr': 'ताಂದೂಳು'},
            'potato': {'hi': 'आलू', 'te': 'బంగాళాదుంప', 'ta': 'உருளைக்கிழங்கு', 'kn': 'ಆಲೂಗಡ್ಡೆ', 'mr': 'बटाटा'},
            'grape': {'hi': 'अंगूर', 'te': 'ద్రాక్ష', 'ta': 'திராட்சை', 'kn': 'ದ್ರಾಕ್ಷಿ', 'mr': 'द्राक्ष'},
            'maize': {'hi': 'मक्का', 'te': 'మొక్కజొన్న', 'ta': 'மக்காச்சோளம்', 'kn': 'ಮೆಕ್ಕೆಜೋಳ', 'mr': 'मका'},
        }
        crop = result['crop'].lower()
        if crop in crop_names and target_language in crop_names[crop]:
            translated['crop_local'] = crop_names[crop][target_language]
        else:
            translated['crop_local'] = translate_text(crop, target_language)
    
    return translated

def translate_disease_info(disease_info: Dict, target_language: str) -> Dict:
    """
    Translate the detailed disease info (symptoms, etc.).
    """
    if target_language == 'en':
        return disease_info
    
    translated = disease_info.copy()
    
    
    if 'description' in disease_info:
        translated['description'] = translate_text(disease_info['description'], target_language)
    
    
    if 'symptoms' in disease_info:
        translated['symptoms'] = translate_text(disease_info['symptoms'], target_language)
    
    
    if 'prevention_steps' in disease_info:
        translated['prevention_steps'] = translate_text(disease_info['prevention_steps'], target_language)
    
    return translated

def translate_pesticide_info(pesticide_info: Dict, target_language: str) -> Dict:
    """
    Translate dosage and instructions for pesticides.
    """
    if target_language == 'en':
        return pesticide_info
    
    translated = pesticide_info.copy()
    
    
    if 'dosage_per_acre' in pesticide_info:
        translated['dosage_per_acre'] = translate_text(pesticide_info['dosage_per_acre'], target_language)
    
    
    if 'frequency' in pesticide_info:
        translated['frequency'] = translate_text(pesticide_info['frequency'], target_language)
    
    
    if 'warnings' in pesticide_info:
        translated['warnings'] = translate_text(pesticide_info['warnings'], target_language)
    
    
    if 'type' in pesticide_info:
        type_translations = {
            'fungicide': {'hi': 'फफूंदनाशक', 'te': 'శిలీంద్ర నాశిని', 'ta': 'பூஞ்சைக் கொல்லி', 'kn': 'ಶಿಲೀಂಧ್ರನಾಶಕ', 'mr': 'बुरशीनाशक'},
            'insecticide': {'hi': 'कीटनाशक', 'te': 'క్రిమి సంహారిణి', 'ta': 'பூச்சிக்கொல்லி', 'kn': 'ಕೀಟನಾಶಕ', 'mr': 'कीटकनाशक'},
            'organic': {'hi': 'जैविक', 'te': 'సేంద్రీయ', 'ta': 'இயற்கை', 'kn': 'ಸಾವಯವ', 'mr': 'सेंद्रिय'}
        }
        pest_type = pesticide_info['type'].lower()
        if pest_type in type_translations and target_language in type_translations[pest_type]:
            translated['type_local'] = type_translations[pest_type][target_language]
    
    return translated

def get_ui_text(key: str, language: str = 'en') -> str:
    """
    Helper to get a single UI text string.
    """
    if language in base_translations and key in base_translations[language]:
        return base_translations[language][key]
    
    
    if 'en' in base_translations and key in base_translations['en']:
        return base_translations['en'][key]
    
    
    return key


# Default English Labels - The master list
UI_LABELS_ENGLISH = {
    "confidence_score": "Confidence Score",
    "severity": "Severity",
    "diagnosis_id": "Diagnosis ID",
    "healthy_crop": "Healthy Crop Detected",
    "potential_disease": "Potential Disease Detected",
    "voice_explanation": "Voice Explanation",
    "pause_explanation": "Pause Explanation",
    "share_report": "Download Report",
    "weather_advice": "Weather-Based Advice",
    "disease_info": "Disease Information",
    "symptoms": "Symptoms",
    "treatment_plan": "Treatment Plan",
    "urgency": "URGENCY",
    "recommended_pesticides": "Recommended Pesticides",
    "dosage": "Dosage",
    "frequency": "Frequency",
    "est_price": "Est. Price",
    "organic": "Organic",
    "chemical": "Chemical",
    "cost_estimation": "Cost Estimation",
    "land_area": "Land Area",
    "treatment_cost": "Treatment Cost",
    "prevention_cost": "Prevention Cost",
    "savings_message": "You could save",
    "prevention_best_practices": "Prevention & Best Practices",
    "organic_alternatives": "Organic Alternatives",
    "finish_diagnosis": "Finish Diagnosis",
    "stage_early": "Early Stage",
    "stage_moderate": "Moderate Stage",
    "stage_severe": "Severe Stage",
    "diagnosis_history_title": "Diagnosis History",
    "no_diagnoses_found": "No diagnoses yet",
    "history_empty_message": "Your past crop diagnoses will appear here.",
    "start_new_diagnosis_btn": "Start New Diagnosis"
}

def get_translated_ui_labels(target_language: str) -> Dict[str, str]:
    """
    Get all the buttons and labels for the app in the user's language.
    Uses batch translation to minimize API round-trips.
    """
    if target_language == 'en':
        return UI_LABELS_ENGLISH

    # Use batch translation: 1 HTTP call instead of 30+
    try:
        batch_results = translate_batch(UI_LABELS_ENGLISH, target_language)
        # Only return labels that are actually different from English
        return {k: v for k, v in batch_results.items() if v and v != UI_LABELS_ENGLISH.get(k)}
    except Exception as e:
        print(f"DEBUG: Batch UI label translation failed: {e}, falling back to English")
        return UI_LABELS_ENGLISH

def get_supported_languages() -> Dict[str, str]:
    """List of languages our app can speak"""
    return {
        'en': 'English',
        'hi': 'हिंदी (Hindi)',
        'te': 'తెలుగు (Telugu)',
        'ta': 'தமிழ் (Tamil)',
        'kn': 'ಕನ್ನಡ (Kannada)',
        'mr': 'मराठी (Marathi)',
        'ml': 'മലയാളം (Malayalam)',
        'tcy': 'ತುಳು (Tulu)'
    }

def get_all_translations(target_language: str) -> Dict[str, str]:
    """
    Get all translations for a specific language.
    Falls back to dynamic translation if key is missing.
    """
    english_dict = base_translations.get('en', {})
    
    # Start with existing manual translations
    if target_language in base_translations:
        result_dict = base_translations[target_language].copy()
    else:
        result_dict = {}
        
    # Fill in missing keys
    for key, en_text in english_dict.items():
        if key not in result_dict:
            # For Tulu, Google Translate doesn't support it well, fallback to English or Kannada?
            # Using English fallback for now as per requirement or specific handling
            if target_language == 'tcy':
                result_dict[key] = en_text 
            else:
                try:
                    # Dynamically translate
                    translated = translate_text(en_text, target_language)
                    result_dict[key] = translated
                except:
                    result_dict[key] = en_text
                    
    return result_dict
