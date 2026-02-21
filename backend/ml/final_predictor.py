from disease_classifier import predict
from severity_estimator import estimate_severity
from stage_classifier import classify_stage

# Where are the brain files (models) for each crop?
MODEL_MAP = {
    "grape": "../models/grape_disease_model.h5",
    "maize": "../models/maize_disease_model.h5",
    "potato": "../models/potato_disease_model.h5",
    "rice": "../models/rice_disease_model.h5",
    "tomato": "../models/tomato_disease_model.h5"
}

# What diseases can we find? (The answers the model can give)
CLASS_NAMES = {
    "grape": [
        "Black Rot",
        "ESCA",
        "Healthy",
        "Leaf Blight"
    ],
    "maize": [
        "Blight",
        "Common_Rust",
        "Gray_Leaf_Spot",
        "Healthy"
    ],
    "potato": [
        "Early Blight",
        "Late Blight",
        "Healthy"
    ],
    "rice": [
        "Bacterial leaf blight",
        "Brown spot",
        "Leaf smut"
    ],
    "tomato": [
        "Healthy",
        "Bacterial spot",
        "Early blight",
        "Late blight",
        "Leaf Mold",
        "Septoria leaf spot",
        "Spider mites Two-spotted spider mite",
        "Target Spot",
        "Tomato Yellow Leaf Curl Virus",
        "Tomato mosaic virus"
    ]
}

def full_prediction(image_path, crop):
    """
    The Master Doctor function! 
    It runs all the tests:
    1. Identify the disease.
    2. Check how bad it is (Severity).
    3. Decide what stage it's in.
    """
    
    # 1. Ask the Disease Classifier
    disease, confidence = predict(
        image_path,
        MODEL_MAP[crop], # Pick the right brain for the crop
        CLASS_NAMES[crop] # Pick the right list of diseases
    )

    
    # Safety Check: If the AI is unsure about Rice, call it Healthy to avoid panic.
    if crop == 'rice' and confidence < 60.0:
        disease = 'Healthy'
        pass

    # 2. Check Severity (How much yellow/brown is there?)
    severity = estimate_severity(image_path)
    
    # 3. Determine Stage (Early, Moderate, or Late?)
    stage = classify_stage(severity)

    # Return the full medical report
    return {
        "crop": crop,
        "disease": disease,
        "confidence": float(round(confidence, 2)),
        "severity_percent": float(severity),
        "stage": stage
    }
