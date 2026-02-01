from flask import Blueprint, request, jsonify
from services.language_service import get_all_translations

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
