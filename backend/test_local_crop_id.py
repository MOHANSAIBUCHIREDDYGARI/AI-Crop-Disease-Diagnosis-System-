"""
Test local crop identification without API key
"""
import sys
import os

# Add paths
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'ml'))

# Temporarily disable API key
original_key = os.environ.get('GOOGLE_GEMINI_API_KEY')
os.environ['GOOGLE_GEMINI_API_KEY'] = ''

from api.routes.chatbot import identify_crop_from_image

def test_local_identification():
    # Test with a sample image
    test_image = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sample.JPG')
    
    if not os.path.exists(test_image):
        print(f"Test image not found: {test_image}")
        return
    
    print("=" * 60)
    print("Testing LOCAL crop identification (no API key)")
    print("=" * 60)
    print(f"Image: {test_image}")
    print()
    
    result = identify_crop_from_image(test_image)
    
    print()
    print("=" * 60)
    if result:
        print(f"✓ SUCCESS: Identified crop as '{result}'")
    else:
        print("✗ FAILED: Could not identify crop")
    print("=" * 60)

if __name__ == "__main__":
    test_local_identification()
    
    # Restore original key
    if original_key:
        os.environ['GOOGLE_GEMINI_API_KEY'] = original_key
