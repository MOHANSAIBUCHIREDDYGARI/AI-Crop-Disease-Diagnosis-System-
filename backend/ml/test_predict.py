import os
from disease_classifier import predict

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

image_path = os.path.join(BASE_DIR, "sample.jpg")
model_path = os.path.join(BASE_DIR, "models", "tomato_disease_model.h5")

class_names = [
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
]

label, confidence = predict(image_path, model_path, class_names)
print("Disease:", label)
print("Confidence:", confidence)
