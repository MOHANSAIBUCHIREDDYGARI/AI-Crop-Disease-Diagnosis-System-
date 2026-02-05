
import sys
import os

print(f"CWD: {os.getcwd()}")
print(f"__file__: {__file__}")

# Mimic chatbot.py append
# chatbot.py is in backend/api/routes/
# we are in backend/
# chatbot logic: sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ml'))
# From backend/verify_imports.py:
ml_path = os.path.join(os.path.dirname(__file__), 'ml')
print(f"Appending path: {ml_path}")
sys.path.append(ml_path)

try:
    import final_predictor
    print("SUCCESS: import final_predictor")
    try:
        from final_predictor import full_prediction
        print("SUCCESS: from final_predictor import full_prediction")
    except ImportError as e:
        print(f"FAILURE: import full_prediction: {e}")
except ImportError as e:
    print(f"FAILURE: import final_predictor: {e}")

try:
    import disease_classifier
    print("SUCCESS: import disease_classifier")
except ImportError as e:
    print(f"FAILURE: import disease_classifier: {e}")
