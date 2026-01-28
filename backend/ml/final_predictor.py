from disease_classifier import predict
from severity_estimator import estimate_severity
from stage_classifier import classify_stage

MODEL_MAP = {
    "tomato": "../models/tomato_disease_model.h5",
    "rice": "../models/rice_disease_model.h5",
    "wheat": "../models/wheat_disease_model.h5",
    "cotton": "../models/cotton_disease_model.h5"
}

CLASS_NAMES = {
    "tomato": [
        "Healthy",
        "Tomato___Bacterial_spot",
        "Tomato___Early_blight",
        "Tomato___Late_blight",
        "Tomato___Leaf_Mold",
        "Tomato___Septoria_leaf_spot",
        "Tomato___Spider_mites Two-spotted_spider_mite",
        "Tomato___Target_Spot",
        "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
        "Tomato___Tomato_mosaic_virus"
    ],
    "rice": ["Healthy", "BrownSpot", "Hispa", "LeafBlast"],
    "wheat": ["Healthy", "Brown rust", "Yellow rust", "Loose Smut"],
    "cotton": ["Healthy", "Bacterial Blight", "Curl Virus", "Leaf Hopper Jassids"]
}

def full_prediction(image_path, crop):
    disease, confidence = predict(
        image_path,
        MODEL_MAP[crop],
        CLASS_NAMES[crop]
    )

    severity = estimate_severity(image_path)
    stage = classify_stage(severity)

    return {
        "crop": crop,
        "disease": disease,
        "confidence": round(confidence, 2),
        "severity_percent": severity,
        "stage": stage
    }
