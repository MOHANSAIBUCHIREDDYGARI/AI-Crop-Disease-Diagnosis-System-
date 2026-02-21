import cv2
import numpy as np

def estimate_severity(image_path):
    """
    Guess how bad the disease is by looking at the leaf colors.
    Note: This is a simple computer vision trick, not deep learning.
    """
    img = cv2.imread(image_path)
    if img is None:
        return 0.0

    # Resize for faster processing so the app doesn't lag
    img = cv2.resize(img, (256, 256))
    
    # Convert to HSV color space 
    # (HSV is better than RGB for separating colors like 'yellow' from 'green')
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define the "diseased" color range (yellows and browns)
    # These numbers define the 'yellow/brown' spectrum in HSV
    lower = np.array([10, 40, 40])
    upper = np.array([35, 255, 255])
    
    # Create a mask: White pixels = diseased area, Black = healthy
    mask = cv2.inRange(hsv, lower, upper)

    # Calculate percentage of the leaf that is "diseased"
    # We count the white pixels in the mask
    severity = (np.count_nonzero(mask) / mask.size) * 100
    
    # Return the clean number (e.g. 45.32)
    return round(severity, 2)
