import cv2
import numpy as np

def estimate_severity(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return 0.0

    img = cv2.resize(img, (256, 256))
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower = np.array([10, 40, 40])
    upper = np.array([35, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)

    severity = (np.count_nonzero(mask) / mask.size) * 100
    return round(severity, 2)
