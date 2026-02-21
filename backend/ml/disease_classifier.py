import cv2
import numpy as np
import tensorflow as tf
import os

def predict(image_path, model_path, class_names):
    """
    The Brain of the AI. 
    It looks at an image and guesses what disease it has.
    """
    try:
        # Basic sanity checks (files exist?)
        if not class_names:
            raise ValueError("class_names cannot be empty")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        print(f"Loading model from: {model_path}")
        
        
        # Load the trained AI model (the .h5 file)
        try:
            model = tf.keras.models.load_model(model_path, compile=False)
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
        
        
        # Figure out how big the model expects the image to be
        input_shape = model.input_shape
        
        
        if isinstance(input_shape, list):
            input_shape = input_shape[0]
            
        target_h, target_w = input_shape[1], input_shape[2]
        channels = input_shape[3] if len(input_shape) > 3 else 3
        
        print(f"Model expects input shape: {input_shape} (H={target_h}, W={target_w}, C={channels})")

        
        # Read the image file using OpenCV
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Image not found or cannot be read: {image_path}")
        
        
        # Prepare the image for the model
        if channels == 1:
            # If model wants black & white
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Add a channel dimension (H, W) -> (H, W, 1)
            img = np.expand_dims(img, axis=-1)
        else:
            # If model wants color (RGB)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        
        # Resize image to fit the model (e.g., 224x224)
        img = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_AREA)
        
        
        if channels == 1 and len(img.shape) == 2:
             img = np.expand_dims(img, axis=-1)
             
        
        # Check if the model handles its own math (normalization)
        has_rescaling = False
        try:
            def check_rescaling(layers):
                for layer in layers:
                    if isinstance(layer, tf.keras.layers.Rescaling):
                        return True
                    if hasattr(layer, 'layers'):
                        if check_rescaling(layer.layers):
                            return True
                return False
            
            has_rescaling = check_rescaling(model.layers)
            print(f"Model has built-in Rescaling layer: {has_rescaling}")
        except Exception as e:
            print(f"Could not check for Rescaling layer: {e}")
            has_rescaling = False

        # If not, we do it manually (scale pixels from 0-255 to 0-1)
        if not has_rescaling:
            img = img.astype(np.float32) / 255.0
            print("Applied manual normalization (1/255)")
        else:
             img = img.astype(np.float32) 
             print("Skipped manual normalization (Model handles it)")
        
        
        # Add a "batch" dimension (Models expect a list of images, even if it's just one)
        img = np.expand_dims(img, axis=0)
        
        
        # Ask the model for its guess!
        preds = model.predict(img, verbose=0)
        print(f"Raw Predictions: {preds}")
        
        # Find the highest score
        idx = np.argmax(preds)
        confidence = np.max(preds) * 100
        
        # Match the score to a name
        if idx >= len(class_names):
            print(f"Warning: Predicted index {idx} out of bounds for class names (len={len(class_names)})")
            disease_name = "Unknown"
        else:
            disease_name = class_names[idx]
        
        print(f"Prediction: {disease_name} ({confidence:.2f}%)")
        return disease_name, confidence
        
    except Exception as e:
        print(f"Error in predict function: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
