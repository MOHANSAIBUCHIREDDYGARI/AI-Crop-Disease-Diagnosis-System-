import cv2
import numpy as np
from tensorflow.keras.models import load_model

CROP_NAMES = ["rice", "wheat", "tomato", "cotton"]

def predict_crop(image_path, model_path):
    model = load_model(model_path)

    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Invalid image path")

    img = cv2.resize(img, (224, 224))
    img = img / 255.0
    img = np.expand_dims(img, axis=0)

    preds = model.predict(img)
    idx = int(np.argmax(preds))

    return CROP_NAMES[idx]
