import requests
import json

def test_translation():
    url = "http://127.0.0.1:5000/api/translations/batch"
    payload = {
        "texts": {
            "hello": "Hello",
            "world": "World",
            "farmer": "Farmer"
        },
        "target_language": "es"
    }
    
    print(f"Testing URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Response:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_translation()
