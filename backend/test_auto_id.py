
import requests
import os
import sys

# Configuration
BASE_URL = "http://127.0.0.1:5000/api/chatbot/message"
IMAGE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sample.JPG"))

def test_automatic_identification():
    print("="*60)
    print("TEST: Automatic Identification (No explicit crop name)")
    print("="*60)

    if not os.path.exists(IMAGE_PATH):
        print(f"ERROR: Sample image not found at {IMAGE_PATH}")
        with open(IMAGE_PATH, 'wb') as f:
            f.write(b'\x00'*1024)
        print(f"Created key image at {IMAGE_PATH} for testing logic (image ID will fail but logic will run)")

    print(f"Sending request to {BASE_URL}...")
    print(f"Message: 'What is wrong with this?' (No crop name)")
    
    try:
        with open(IMAGE_PATH, 'rb') as img:
            files = {'image': img}
            data = {'message': 'What is wrong with this?'}
            
            response = requests.post(BASE_URL, files=files, data=data)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                json_resp = response.json()
                bot_response = json_resp.get('response', '')
                print("-" * 30)
                print("Bot Response Preview:")
                print(bot_response[:300] + "...")
                print("-" * 30)
                
                if "diagnosis system detected" in bot_response:
                    print("SUCCESS: Automatic identification worked!")
                elif "could not automatically identify" in bot_response:
                    print("FAILURE: Fallback triggered (Auto ID failed).")
                else:
                    print("UNCERTAIN: Check response manually.")
            else:
                print(f"FAILURE: Error {response.status_code}")
                print(response.text)

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_automatic_identification()
