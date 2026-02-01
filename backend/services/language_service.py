from googletrans import Translator
from typing import Optional, Dict
import json
import os

# Initialize translator
translator = Translator()

# Cache for translations to reduce API calls
translation_cache = {}

# Load base translations from file
TRANSLATIONS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'database', 'seed', 'translations.json'
)

def load_base_translations() -> Dict:
    """Load base UI translations from file"""
    try:
        if os.path.exists(TRANSLATIONS_FILE):
            with open(TRANSLATIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading translations: {e}")
    return {}

base_translations = load_base_translations()

def translate_text(text: str, target_language: str = 'en', source_language: str = 'en') -> str:
    """
    Translate text to target language using Google Translate
    
    Args:
        text: Text to translate
        target_language: Target language code (hi, te, ta, etc.)
        source_language: Source language code (default: en)
        
    Returns:
        Translated text
    """
    # If target is same as source, return original
    if target_language == source_language or target_language == 'en':
        return text
    
    # Check cache first
    cache_key = f"{text}_{source_language}_{target_language}"
    if cache_key in translation_cache:
        return translation_cache[cache_key]
    
    try:
        # Translate using googletrans library (free)
        translation = translator.translate(text, src=source_language, dest=target_language)
        translated_text = translation.text
        
        # Cache the translation
        translation_cache[cache_key] = translated_text
        
        return translated_text
    except Exception as e:
        print(f"Translation error: {e}")
        # Return original text if translation fails
        return text

def translate_diagnosis_result(result: Dict, target_language: str) -> Dict:
    """
    Translate diagnosis result to target language
    
    Args:
        result: Diagnosis result dictionary
        target_language: Target language code
        
    Returns:
        Translated result dictionary
    """
    if target_language == 'en':
        return result
    
    translated = result.copy()
    
    # Translate disease name (keep original format for reference)
    if 'disease' in result:
        translated['disease_local'] = translate_text(
            result['disease'].replace('___', ' - ').replace('_', ' '),
            target_language
        )
    
    # Translate stage
    if 'stage' in result:
        translated['stage_local'] = translate_text(result['stage'], target_language)
    
    # Translate crop name
    if 'crop' in result:
        crop_names = {
            'tomato': {'hi': 'टमाटर', 'te': 'టమాటా', 'ta': 'தக்காளி', 'kn': 'ಟೊಮೇಟೊ', 'mr': 'टोमॅटो'},
            'rice': {'hi': 'चावल', 'te': 'వరి', 'ta': 'அரிசி', 'kn': 'ಅಕ್ಕಿ', 'mr': 'तांदूळ'},
            'wheat': {'hi': 'गेहूं', 'te': 'గోధుమ', 'ta': 'கோதுமை', 'kn': 'ಗೋಧಿ', 'mr': 'गहू'},
            'cotton': {'hi': 'कपास', 'te': 'పత్తి', 'ta': 'பருத்தி', 'kn': 'ಹತ್ತಿ', 'mr': 'कापूस'}
        }
        crop = result['crop'].lower()
        if crop in crop_names and target_language in crop_names[crop]:
            translated['crop_local'] = crop_names[crop][target_language]
        else:
            translated['crop_local'] = translate_text(crop, target_language)
    
    return translated

def translate_disease_info(disease_info: Dict, target_language: str) -> Dict:
    """
    Translate disease information (description, symptoms, prevention)
    
    Args:
        disease_info: Disease information dictionary
        target_language: Target language code
        
    Returns:
        Translated disease information
    """
    if target_language == 'en':
        return disease_info
    
    translated = disease_info.copy()
    
    # Translate description
    if 'description' in disease_info:
        translated['description'] = translate_text(disease_info['description'], target_language)
    
    # Translate symptoms
    if 'symptoms' in disease_info:
        translated['symptoms'] = translate_text(disease_info['symptoms'], target_language)
    
    # Translate prevention steps
    if 'prevention_steps' in disease_info:
        translated['prevention_steps'] = translate_text(disease_info['prevention_steps'], target_language)
    
    return translated

def translate_pesticide_info(pesticide_info: Dict, target_language: str) -> Dict:
    """
    Translate pesticide information
    
    Args:
        pesticide_info: Pesticide information dictionary
        target_language: Target language code
        
    Returns:
        Translated pesticide information
    """
    if target_language == 'en':
        return pesticide_info
    
    translated = pesticide_info.copy()
    
    # Translate dosage
    if 'dosage_per_acre' in pesticide_info:
        translated['dosage_per_acre'] = translate_text(pesticide_info['dosage_per_acre'], target_language)
    
    # Translate frequency
    if 'frequency' in pesticide_info:
        translated['frequency'] = translate_text(pesticide_info['frequency'], target_language)
    
    # Translate warnings
    if 'warnings' in pesticide_info:
        translated['warnings'] = translate_text(pesticide_info['warnings'], target_language)
    
    # Translate type
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
    Get UI text in specified language
    
    Args:
        key: Translation key
        language: Language code
        
    Returns:
        Translated UI text
    """
    if language in base_translations and key in base_translations[language]:
        return base_translations[language][key]
    
    # Fallback to English
    if 'en' in base_translations and key in base_translations['en']:
        return base_translations['en'][key]
    
    # Return key if not found
    return key

def get_supported_languages() -> Dict[str, str]:
    """Get list of supported languages"""
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
