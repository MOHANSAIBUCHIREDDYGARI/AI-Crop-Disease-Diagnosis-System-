
import sys
import os
import cv2
import numpy as np

# Add ml path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ml'))

from final_predictor import full_prediction

IMAGE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sample.JPG"))

def test_brute_force_id():
    print("="*60)
    print("TEST: Brute Force Crop Identification")
    print("="*60)
    
    supported_crops = ['tomato', 'rice', 'wheat', 'cotton']
    
    if not os.path.exists(IMAGE_PATH):
        print(f"Sample image not found: {IMAGE_PATH}")
        return

    results = []
    
    print(f"Testing image: {IMAGE_PATH}")
    
    for crop in supported_crops:
        try:
            print(f"Running model for: {crop}...")
            # Note: We need to be careful about paths in full_prediction as it uses relative paths
            # This script is in backend/, models are in ../models/
            # final_predictor expects models in ../models/ relative to itself (backend/ml/)
            # So running from backend/ should work if imports are correct.
            
            result = full_prediction(IMAGE_PATH, crop)
            print(f"  -> Result: {result['disease']} (Confidence: {result['confidence']}%)")
            results.append(result)
        except Exception as e:
            print(f"  -> Error for {crop}: {e}")

    if not results:
        print("No successful predictions.")
        return

    # Find best match
    best_match = max(results, key=lambda x: x['confidence'])
    print("-" * 30)
    print(f"BEST MATCH: {best_match['crop'].upper()}")
    print(f"Disease: {best_match['disease']}")
    print(f"Confidence: {best_match['confidence']}%")
    print("-" * 30)

if __name__ == "__main__":
    test_brute_force_id()
