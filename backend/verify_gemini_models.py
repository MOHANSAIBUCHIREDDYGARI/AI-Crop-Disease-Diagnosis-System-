
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load env
base_path = os.path.dirname(__file__)
env_path = os.path.join(base_path, '.env')
load_dotenv(env_path)

api_key = os.getenv('GOOGLE_GEMINI_API_KEY')

print(f"API Key found: {bool(api_key)}")

if api_key:
    genai.configure(api_key=api_key)
    try:
        print("Listing available models...")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
    except Exception as e:
        print(f"Error listing models: {e}")

    print("\nTesting gemini-pro-vision (fallback)...")
    try:
        model = genai.GenerativeModel('gemini-pro-vision')
        print("Model gemini-pro-vision initialized successfully.")
    except Exception as e:
        print(f"Error initializing gemini-pro-vision: {e}")

else:
    print("No API Key.")
