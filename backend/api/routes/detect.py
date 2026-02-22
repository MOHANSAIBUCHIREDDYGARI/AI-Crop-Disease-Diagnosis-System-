from flask import request, jsonify
# We use TensorFlow to run our AI model
from tensorflow.keras.models import load_model
import numpy as np
import cv2
from ml.severity_estimator import estimate_severity

# Load the trained model - this is our "brain" that detects diseases!
model = load_model("models/disease_classifier.h5")

def predict_disease(image_path):
    # Read the image file so we can process it
    img = cv2.imread(image_path)
    
    # Resize the image to 224x224 pixels because that's what our model expects
    img = cv2.resize(img, (224, 224))
    
    # Normalize pixel values to be between 0 and 1 (helps the AI learn better)
    img = img / 255.0
    
    # Add an extra dimension because the model expects a batch of images, not just one
    img = np.expand_dims(img, axis=0)

    # Ask the model to predict what disease this is
    preds = model.predict(img)
    
    # Find the disease with the highest probability
    class_index = np.argmax(preds)
    
    # Calculate how confident the model is (0 to 100%)
    confidence = round(float(np.max(preds)) * 100, 2)

    return class_index, confidence
