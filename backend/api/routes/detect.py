from flask import request, jsonify
from tensorflow.keras.models import load_model
import numpy as np
import cv2
from ml.severity_estimator import estimate_severity

model = load_model("models/disease_classifier.h5")

def predict_disease(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, (224, 224))
    img = img / 255.0
    img = np.expand_dims(img, axis=0)

    preds = model.predict(img)
    class_index = np.argmax(preds)
    confidence = round(float(np.max(preds)) * 100, 2)

    return class_index, confidence
