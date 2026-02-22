import cv2
import numpy as np

def preprocess_image(image_path: str, target_size: tuple = (224, 224)) -> np.ndarray:
    """
    Preprocess image for model prediction
    Handles different lighting conditions and normalizes the image
    
    Args:
        image_path: Path to the image file
        target_size: Target size for the model (width, height)
        
    Returns:
        Preprocessed image array ready for prediction
    """
    
    img = cv2.imread(image_path)
    
    
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    
    img = auto_white_balance(img)
    
    
    h, w = img.shape[:2]
    
    
    if h < w:
        new_h = target_size[1]
        new_w = int(w * (target_size[1] / h))
    else:
        new_w = target_size[0]
        new_h = int(h * (target_size[0] / w))
    
    img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    
    h, w = img.shape[:2]
    start_y = (h - target_size[1]) // 2
    start_x = (w - target_size[0]) // 2
    img = img[start_y:start_y+target_size[1], start_x:start_x+target_size[0]]
    
    
    img_array = np.array(img, dtype=np.float32)
    img_array = img_array / 255.0  
    
    
    img_array = np.expand_dims(img_array, axis=0)
    
    return img_array

def auto_white_balance(img: np.ndarray) -> np.ndarray:
    """
    Apply automatic white balance to handle different lighting conditions
    
    Args:
        img: Input image in RGB format
        
    Returns:
        White-balanced image
    """
    
    avg_b = np.mean(img[:, :, 0])
    avg_g = np.mean(img[:, :, 1])
    avg_r = np.mean(img[:, :, 2])
    
    
    avg_gray = (avg_b + avg_g + avg_r) / 3
    
    
    scale_b = avg_gray / avg_b if avg_b > 0 else 1.0
    scale_g = avg_gray / avg_g if avg_g > 0 else 1.0
    scale_r = avg_gray / avg_r if avg_r > 0 else 1.0
    
    
    balanced = img.copy().astype(np.float32)
    balanced[:, :, 0] = np.clip(balanced[:, :, 0] * scale_b, 0, 255)
    balanced[:, :, 1] = np.clip(balanced[:, :, 1] * scale_g, 0, 255)
    balanced[:, :, 2] = np.clip(balanced[:, :, 2] * scale_r, 0, 255)
    
    return balanced.astype(np.uint8)

def adjust_brightness_contrast(img: np.ndarray, brightness: int = 0, contrast: int = 0) -> np.ndarray:
    """
    Adjust brightness and contrast of image
    
    Args:
        img: Input image
        brightness: Brightness adjustment (-100 to 100)
        contrast: Contrast adjustment (-100 to 100)
        
    Returns:
        Adjusted image
    """
    
    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness
        alpha_b = (highlight - shadow) / 255
        gamma_b = shadow
        img = cv2.addWeighted(img, alpha_b, img, 0, gamma_b)
    
    
    if contrast != 0:
        alpha_c = 131 * (contrast + 127) / (127 * (131 - contrast))
        gamma_c = 127 * (1 - alpha_c)
        img = cv2.addWeighted(img, alpha_c, img, 0, gamma_c)
    
    return img

def remove_background(img: np.ndarray) -> np.ndarray:
    """
    Remove background to focus on plant/leaf
    
    Args:
        img: Input image in RGB format
        
    Returns:
        Image with background removed
    """
    
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    
    
    lower_green = np.array([25, 40, 40])
    upper_green = np.array([90, 255, 255])
    
    
    mask = cv2.inRange(hsv, lower_green, upper_green)
    
    
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    
    result = cv2.bitwise_and(img, img, mask=mask)
    
    
    background = np.ones_like(img) * 255
    background[mask > 0] = result[mask > 0]
    
    return background

def augment_image(img: np.ndarray, rotation: int = 0, flip: bool = False) -> np.ndarray:
    """
    Apply data augmentation to image
    
    Args:
        img: Input image
        rotation: Rotation angle in degrees
        flip: Whether to flip horizontally
        
    Returns:
        Augmented image
    """
    
    if rotation != 0:
        height, width = img.shape[:2]
        center = (width // 2, height // 2)
        matrix = cv2.getRotationMatrix2D(center, rotation, 1.0)
        img = cv2.warpAffine(img, matrix, (width, height))
    
    
    if flip:
        img = cv2.flip(img, 1)
    
    return img

def preprocess_for_severity(image_path: str) -> np.ndarray:
    """
    Preprocess image specifically for severity estimation
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Preprocessed image for severity analysis
    """
    
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    
    img = cv2.resize(img, (224, 224))
    
    
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    
    return hsv
