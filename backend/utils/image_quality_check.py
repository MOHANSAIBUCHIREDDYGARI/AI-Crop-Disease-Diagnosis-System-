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
        # Read image
        img = cv2.imread(image_path)
        
        if img is None:
            return {
                'is_valid': False,
                'reason': 'Unable to read image file',
                'quality_score': 0.0
            }
        
        # Check image size
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
        
        # Calculate blur score using Laplacian variance
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Normalize blur score (higher is sharper)
        # Typical values: <100 = very blurry, 100-500 = acceptable, >500 = sharp
        blur_score = min(laplacian_var / 500.0, 1.0)
        
        # Calculate brightness score
        brightness = np.mean(gray)
        # Ideal brightness is around 127 (middle gray)
        brightness_score = 1.0 - abs(brightness - 127) / 127.0
        
        # Calculate contrast score
        contrast = np.std(gray)
        # Normalize contrast (higher is better, typical range 0-100)
        contrast_score = min(contrast / 50.0, 1.0)
        
        # Calculate overall quality score (weighted average)
        quality_score = (
            blur_score * 0.5 +        # Blur is most important
            brightness_score * 0.25 +  # Brightness matters
            contrast_score * 0.25      # Contrast helps
        )
        
        # Determine if image passes quality check
        # Relaxed thresholds for real-world mobile photos
        min_quality_threshold = 0.2
        min_blur_threshold = 0.15
        is_valid = quality_score >= min_quality_threshold and blur_score >= min_blur_threshold
        
        # Log quality metrics for debugging
        print(f"DEBUG: Image quality check - Quality: {quality_score:.3f}, Blur: {blur_score:.3f}, "
              f"Brightness: {brightness_score:.3f}, Contrast: {contrast_score:.3f}, "
              f"Valid: {is_valid}")
        
        result = {
            'is_valid': is_valid,
            'quality_score': round(quality_score, 3),
            'blur_score': round(blur_score, 3),
            'brightness_score': round(brightness_score, 3),
            'contrast_score': round(contrast_score, 3),
            'dimensions': (width, height),
            'brightness': round(brightness, 1),
            'laplacian_variance': round(laplacian_var, 1)
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
    
    # Convert to LAB color space
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to L channel
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    
    # Merge channels
    enhanced_lab = cv2.merge([l, a, b])
    
    # Convert back to BGR
    enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
    
    # Apply slight sharpening
    kernel = np.array([[-1, -1, -1],
                       [-1,  9, -1],
                       [-1, -1, -1]])
    enhanced = cv2.filter2D(enhanced, -1, kernel)
    
    # Save enhanced image
    if output_path is None:
        output_path = image_path.replace('.', '_enhanced.')
    
    cv2.imwrite(output_path, enhanced)
    
    return output_path
