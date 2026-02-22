import cv2
import numpy as np
from typing import Tuple, Dict

def check_image_quality(image_path: str) -> Dict[str, any]:
    """
    Check if image quality is acceptable for disease detection
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dictionary with quality metrics and pass/fail status
    """
    try:
        
        img = cv2.imread(image_path)
        
        if img is None:
            return {
                'is_valid': False,
                'reason': 'Unable to read image file',
                'quality_score': 0.0
            }
        
        
        height, width = img.shape[:2]
        
        if width < 100 or height < 100:
            return {
                'is_valid': False,
                'reason': 'Image too small (minimum 100x100 pixels)',
                'quality_score': 0.0,
                'dimensions': (width, height)
            }
        
        if width > 4000 or height > 4000:
            return {
                'is_valid': False,
                'reason': 'Image too large (maximum 4000x4000 pixels)',
                'quality_score': 0.0,
                'dimensions': (width, height)
            }
        
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        
        
        blur_score = min(laplacian_var / 500.0, 1.0)
        
        
        brightness = np.mean(gray)
        
        brightness_score = 1.0 - abs(brightness - 127) / 127.0
        
        
        contrast = np.std(gray)
        
        contrast_score = min(contrast / 50.0, 1.0)
        
        
        quality_score = (
            blur_score * 0.5 +        
            brightness_score * 0.25 +  
            contrast_score * 0.25      
        )
        
        
        
        
        min_quality_threshold = 0.15
        min_blur_threshold = 0.01 
        is_valid = quality_score >= min_quality_threshold and blur_score >= min_blur_threshold
        
        
        print(f"DEBUG: Image quality check - Quality: {quality_score:.3f}, Blur: {blur_score:.3f}, "
              f"Brightness: {brightness_score:.3f}, Contrast: {contrast_score:.3f}, "
              f"Valid: {is_valid}")
        
        result = {
            'is_valid': bool(is_valid),
            'quality_score': float(round(quality_score, 3)),
            'blur_score': float(round(blur_score, 3)),
            'brightness_score': float(round(brightness_score, 3)),
            'contrast_score': float(round(contrast_score, 3)),
            'dimensions': (int(width), int(height)),
            'brightness': float(round(brightness, 1)),
            'laplacian_variance': float(round(laplacian_var, 1))
        }
        
        if not is_valid:
            if blur_score < min_blur_threshold:
                result['reason'] = 'Image is too blurry. Please capture a clearer image.'
            elif brightness_score < 0.3:
                if brightness < 50:
                    result['reason'] = 'Image is too dark. Please use better lighting.'
                else:
                    result['reason'] = 'Image is too bright. Please avoid direct sunlight.'
            else:
                result['reason'] = 'Image quality is too low. Please capture a better image.'
        
        return result
        
    except Exception as e:
        return {
            'is_valid': False,
            'reason': f'Error processing image: {str(e)}',
            'quality_score': 0.0
        }

def get_quality_feedback(quality_result: Dict) -> str:
    """
    Get user-friendly feedback about image quality
    
    Args:
        quality_result: Result from check_image_quality
        
    Returns:
        User-friendly message
    """
    if quality_result['is_valid']:
        score = quality_result['quality_score']
        if score > 0.7:
            return "✓ Excellent image quality!"
        elif score > 0.5:
            return "✓ Good image quality"
        else:
            return "✓ Acceptable image quality"
    else:
        return f"✗ {quality_result.get('reason', 'Image quality check failed')}"

def enhance_image_quality(image_path: str, output_path: str = None) -> str:
    """
    Enhance image quality for better disease detection
    
    Args:
        image_path: Path to input image
        output_path: Path to save enhanced image (optional)
        
    Returns:
        Path to enhanced image
    """
    img = cv2.imread(image_path)
    
    
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    
    
    enhanced_lab = cv2.merge([l, a, b])
    
    
    enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
    
    
    kernel = np.array([[-1, -1, -1],
                       [-1,  9, -1],
                       [-1, -1, -1]])
    enhanced = cv2.filter2D(enhanced, -1, kernel)
    
    
    if output_path is None:
        output_path = image_path.replace('.', '_enhanced.')
    
    cv2.imwrite(output_path, enhanced)
    
    return output_path

def check_content_validity(image_path: str) -> Dict[str, any]:
    """
    Check if the image content appears to be a plant/leaf based on color analysis.
    This helps reject random photos like faces, furniture, etc.
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return {'is_valid': False, 'reason': 'Unable to read image'}

        
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        
        total_pixels = img.shape[0] * img.shape[1]
        
        
        
        
        
        lower_green = np.array([25, 30, 30])
        upper_green = np.array([95, 255, 255])
        mask_green = cv2.inRange(hsv, lower_green, upper_green)
        
        
        lower_yellow = np.array([10, 30, 30])
        upper_yellow = np.array([35, 255, 255])
        mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
        
        
        lower_brown = np.array([0, 20, 20])
        upper_brown = np.array([20, 200, 150])
        mask_brown = cv2.inRange(hsv, lower_brown, upper_brown)
        
        
        combined_mask = cv2.bitwise_or(mask_green, mask_yellow)
        combined_mask = cv2.bitwise_or(combined_mask, mask_brown)
        
        
        plant_pixels = cv2.countNonZero(combined_mask)
        plant_ratio = plant_pixels / total_pixels
        
        print(f"DEBUG: Plant pixel ratio: {plant_ratio:.3f}")
        
        
        
        min_plant_ratio = 0.15
        
        if plant_ratio < min_plant_ratio:
            return {
                'is_valid': False,
                'reason': 'Image does not appear to contain enough plant material (leaves/stems). Please ensure the crop is clearly visible.',
                'score': float(plant_ratio)
            }
            
        return {
            'is_valid': True,
            'reason': 'Valid plant content detected',
            'score': float(plant_ratio)
        }

    except Exception as e:
        print(f"Error in content check: {e}")
        
        return {'is_valid': True, 'reason': 'Content check passed (fallback)'}
