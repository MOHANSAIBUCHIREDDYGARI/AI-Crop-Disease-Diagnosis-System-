import sys
import os

# Add project root to path
# Add project root and backend directory to path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # This is 'backend' folder
root_dir = os.path.dirname(base_dir) # This is project root

sys.path.append(base_dir)
sys.path.append(root_dir)

from api.routes.chatbot import get_fallback_response

def test_chatbot_responses():
    test_cases = [
        ("How to treat potato early blight?", "potato_early_blight"),
        ("My potato leaves have dark water soaked spots", "potato_late_blight"),
        ("Wheat has yellow pustules (rust)", "wheat_rust"),
        ("Maize common rust treatment", "maize_rust"),
        ("Cotton bacterial blight cure", "cotton_blight"),
        ("Grape black rot symptoms", "grape_rot"),
        ("Rice blast fungicide", "rice_blast"),
        ("Tomato early blight", "tomato_early_blight")
    ]
    
    print("Testing Chatbot Fallback Logic...\n")
    
    with open("test_result.log", "w", encoding="utf-8") as f:
        passed = 0
        for question, expected_key in test_cases:
            response = get_fallback_response(question)
            
            # Check if response contains key words related to the expected topic
            if expected_key == 'potato_early_blight' and "Early Blight in Potato" in response:
                f.write(f"PASS: {question}\n")
                passed += 1
            elif expected_key == 'potato_late_blight' and "Late Blight in Potato" in response:
                 f.write(f"PASS: {question}\n")
                 passed += 1
            elif expected_key == 'wheat_rust' and "Rust in Wheat" in response:
                 f.write(f"PASS: {question}\n")
                 passed += 1
            elif expected_key == 'maize_rust' and "Common Rust in Maize" in response:
                 f.write(f"PASS: {question}\n")
                 passed += 1
            elif expected_key == 'cotton_blight' and "Bacterial Blight in Cotton" in response:
                 f.write(f"PASS: {question}\n")
                 passed += 1
            elif expected_key == 'grape_rot' and "Black Rot in Grape" in response:
                 f.write(f"PASS: {question}\n")
                 passed += 1
            elif expected_key == 'rice_blast' and "Rice Blast" in response:
                 f.write(f"PASS: {question}\n")
                 passed += 1
            elif expected_key == 'tomato_early_blight' and "Early Blight in tomato" in response:
                 f.write(f"PASS: {question}\n")
                 passed += 1
            else:
                f.write(f"FAIL: {question} - Expected key {expected_key}\n")
                f.write(f"Response was: {response}\n")

        f.write(f"\nResult: {passed}/{len(test_cases)} passed.\n")
        print(f"Result: {passed}/{len(test_cases)} passed. Check test_result.log for details.")

if __name__ == "__main__":
    test_chatbot_responses()
