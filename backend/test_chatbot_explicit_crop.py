
import requests
import os
import sys

# Configuration
BASE_URL = "http://127.0.0.1:5000/api/chatbot/message"
IMAGE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sample.JPG"))

def test_explicit_crop_diagnosis():
    print("="*60)
    print("TEST: Chatbot Diagnosis with Explicit Crop Name")
    print("="*60)

    # 1. Verify image exists
    if not os.path.exists(IMAGE_PATH):
        print(f"ERROR: Sample image not found at {IMAGE_PATH}")
        # Create a dummy image if not exists
        with open(IMAGE_PATH, 'wb') as f:
            f.write(b'\x00'*1024)
        print(f"Created dummy image at {IMAGE_PATH}")

    # 2. Send request with "tomato" in message
    print(f"Sending request to {BASE_URL}...")
    print(f"Message: 'Check this tomato plant'")
    print(f"Image: {IMAGE_PATH}")

    try:
        with open(IMAGE_PATH, 'rb') as img:
            files = {'image': img}
            data = {'message': 'Check this tomato plant'}
            
            response = requests.post(BASE_URL, files=files, data=data)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                json_resp = response.json()
                bot_response = json_resp.get('response', '')
                
                print("-" * 30)
                print("Bot Response Preview:")
                print(bot_response[:200] + "...")
                print("-" * 30)
                
                # Validation Logic
                # We look for keywords indicating diagnosis happened
                # e.g., "detected:", "severity", "Monitor", or specific disease names
                # The code I added: 
                # context += f" My diagnosis system detected: {prediction_result['disease']}..."
                
                if "detected:" in bot_response or "diagnosis system" in bot_response:
                    print("SUCCESS: Diagnosis triggered explicitly!")
                elif "I could not automatically identify the crop" in bot_response:
                    print("FAILURE: Fallback logic triggered (explicit crop name ignored).")
                else:
                    print("UNCERTAIN: Check response manually.")
            else:
                print("FAILURE: Server returned error.")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_explicit_crop_diagnosis()
