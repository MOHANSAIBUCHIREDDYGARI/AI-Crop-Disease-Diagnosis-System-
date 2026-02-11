import json
import os
import concurrent.futures
from deep_translator import GoogleTranslator
from config.settings import settings

# Path to the translations cache file
CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache', 'translations_cache.json')

def load_cache():
    """Load translations from the JSON cache file."""
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading translation cache: {e}")
        return {}

def save_cache(cache):
    """Save translations to the JSON cache file."""
    try:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving translation cache: {e}")

def get_all_translations(language):
    """
    Get all translations for a specific language from the cache.
    Returns a dictionary of key-value pairs.
    """
    cache = load_cache()
    return cache.get(language, {})

def translate_chunk(chunk, target_language):
    """
    Translate a small chunk of texts.
    chunk: dict of {key: text}
    """
    translator = GoogleTranslator(source='auto', target=target_language)
    translated_chunk = {}
    
    # deep_translator's translate_batch takes a list of strings
    keys = list(chunk.keys())
    texts = list(chunk.values())
    
    try:
        # Check if texts is empty
        if not texts:
            return {}
            
        translated_texts = translator.translate_batch(texts)
        
        for i, key in enumerate(keys):
            translated_chunk[key] = translated_texts[i]
            
    except Exception as e:
        print(f"Error translating chunk: {e}")
        # Fallback: return original text or error indicator
        for key, text in chunk.items():
            translated_chunk[key] = text 
            
    return translated_chunk

def translate_batch(texts, target_language):
    """
    Translate a batch of texts using parallel processing.
    texts: dict of {key: text} where key is the ID and text is the content to translate
    target_language: language code (e.g., 'es', 'hi')
    """
    if not texts or target_language == 'en':
        return texts

    cache = load_cache()
    if target_language not in cache:
        cache[target_language] = {}
    
    language_cache = cache[target_language]
    missing_texts = set()
    results = {}
    
    # Identify what needs to be translated (check cache by TEXT value, not key)
    for key, text in texts.items():
        if not text:
            results[key] = ""
            continue
            
        # Check if the text itself is in the cache
        if text in language_cache:
            results[key] = language_cache[text]
        else:
            missing_texts.add(text)
            
    if not missing_texts:
        # All found in cache
        return results
    
    # Process missing translations in parallel chunks
    # Chunk size of 5 for parallel execution as requested
    BATCH_SIZE = 5
    chunks = []
    missing_list = list(missing_texts)
    
    for i in range(0, len(missing_list), BATCH_SIZE):
        # Create a dict chunk for the translator helper: {original_text: original_text}
        # The helper expects {key: text}, so we use text as key to easily map back
        chunk_items = {text: text for text in missing_list[i:i + BATCH_SIZE]}
        chunks.append(chunk_items)
        
    print(f"Translating {len(missing_texts)} unique items in {len(chunks)} parallel batches...")
    
    new_translations = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_chunk = {executor.submit(translate_chunk, chunk, target_language): chunk for chunk in chunks}
        
        for future in concurrent.futures.as_completed(future_to_chunk):
            try:
                result = future.result()
                new_translations.update(result)
            except Exception as e:
                print(f"Chunk translation failed: {e}")
                
    # Update cache
    language_cache.update(new_translations)
    cache[target_language] = language_cache
    save_cache(cache)
    
    # Populate results for the missing items from the now-updated cache (or new_translations directly)
    for key, text in texts.items():
        if key not in results: # It was missing
            results[key] = new_translations.get(text, text) # Fallback to original if completely failed
        
    return results

def translate_diagnosis_result(result, target_language):
    """
    Translate diagnosis result fields.
    result: dict containing 'disease', 'stage', etc.
    """
    if target_language == 'en':
        return result
        
    # Fields to translate
    fields_to_translate = {}
    if 'disease' in result:
        fields_to_translate['disease'] = result['disease']
    if 'stage' in result:
        fields_to_translate['stage'] = result['stage']
        
    if not fields_to_translate:
        return result
        
    translated = translate_batch(fields_to_translate, target_language)
    
    # Update result with translations
    new_result = result.copy()
    for key, value in translated.items():
        new_result[key] = value
        
    return new_result

def translate_disease_info(info, target_language):
    """
    Translate disease information fields.
    info: dict containing 'description', 'symptoms', 'prevention_steps'
    """
    if target_language == 'en':
        return info
        
    # Fields to translate
    fields_to_translate = {}
    if 'description' in info:
        fields_to_translate['description'] = info['description']
    if 'symptoms' in info:
        fields_to_translate['symptoms'] = info['symptoms']
    if 'prevention_steps' in info:
        fields_to_translate['prevention_steps'] = info['prevention_steps']
        
    if not fields_to_translate:
        return info
        
    translated = translate_batch(fields_to_translate, target_language)
    
    # Update info with translations
    new_info = info.copy()
    for key, value in translated.items():
        new_info[key] = value
        
    return new_info

def translate_text(text, target_language, source_language='auto'):
    """
    Translate a single text string.
    """
    if not text:
        return ""
    if target_language == 'en' and source_language == 'en':
        return text
        
    # Check cache first
    cache = load_cache()
    if target_language in cache and text in cache[target_language]:
        return cache[target_language][text]
        
    # Translate
    try:
        translator = GoogleTranslator(source=source_language, target=target_language)
        translated_text = translator.translate(text)
        
        # Update cache
        if target_language not in cache:
            cache[target_language] = {}
        cache[target_language][text] = translated_text
        save_cache(cache)
        
        return translated_text
    except Exception as e:
        print(f"Error translating text: {e}")
        return text

def get_translated_ui_labels(target_language):
    """
    Retrieves all translated UI labels for a given language.
    This is essentially a wrapper around get_all_translations,
    exposed for the user API to fetch entire translation sets.
    """
    return get_all_translations(target_language)
