from services.language_service import translate_batch
import json

def test_logic():
    texts = {
        "hello": "Hello",
        "farmer": "Farmer",
        "crop": "Crop"
    }
    target = "es"
    
    print("Testing translate_batch logic...")
    try:
        results = translate_batch(texts, target)
        print("Results:")
        print(json.dumps(results, indent=2))
        
        if results.get('hello') == 'Hola':
            print("SUCCESS: Translation looks correct.")
        else:
            print("WARNING: unexpected translation.")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test_logic()
