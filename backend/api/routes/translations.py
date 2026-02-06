from flask import Blueprint, request, jsonify
from services.language_service import get_all_translations, translate_batch

translations_bp = Blueprint('translations', __name__)

@translations_bp.route('/', methods=['GET'])
def get_translations():
    """
    Get all UI translations for a specified language.
    Falls back to dynamic translation if keys are missing in the static file.
    """
    try:
        language = request.args.get('language', 'en')
        translations = get_all_translations(language)
        return jsonify(translations), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@translations_bp.route('/batch', methods=['POST'])
def batch_translate():
    """
    Translate a batch of texts
    """
    try:
        data = request.get_json()
        print(f"DEBUG: Received batch translation request: {data.keys()}")
        
        texts = data.get('texts', {})
        target_language = data.get('target_language', 'en')
        
        print(f"DEBUG: Translating {len(texts)} items to '{target_language}'")
        
        translated_texts = translate_batch(texts, target_language)
        
        # print(f"DEBUG: Translation result (first 3): {list(translated_texts.items())[:3]}")
        
        return jsonify(translated_texts), 200
        
    except Exception as e:
        print(f"Batch translation error: {e}")
        return jsonify({'error': str(e)}), 500
