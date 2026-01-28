import cv2
import numpy as np
import tensorflow as tf
import os

def build_mobilenet_model(num_classes):
    """
    Reconstructs the model architecture used during training.
    Based on the inspection, it's MobileNetV2 -> GlobalAveragePooling2D -> Dropout -> Dense
    """
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights=None
    )
    
    x = base_model.output
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    output = tf.keras.layers.Dense(num_classes, activation='softmax')(x)
    
    model = tf.keras.models.Model(inputs=base_model.input, outputs=output)
    model.trainable = False  # Set to inference mode
    
    return model

def predict(image_path, model_path, class_names):
    try:
        # Input validation
        if not class_names:
            raise ValueError("class_names cannot be empty")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        print(f"Loading weights from: {model_path}")
        
        # 1. Rebuild the model architecture
        num_classes = len(class_names)
        print(f"Rebuilding MobileNetV2 for {num_classes} classes...")
        model = build_mobilenet_model(num_classes)
        
        # 2. Load weights
        try:
            model.load_weights(model_path)
        except Exception as w_err:
            print(f"Standard load failed, trying by_name: {w_err}")
            model.load_weights(model_path, by_name=True, skip_mismatch=True)
        
        print("Model weights loaded successfully!")
        
        # 3. Read and preprocess image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Image not found or cannot be read: {image_path}")
        
        # CRITICAL: Convert BGR to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Center crop preprocessing (preserves aspect ratio without padding)
        # This is a common technique in image classification
        h, w = img.shape[:2]
        target_size = 224
        
        # Resize so smaller dimension = target_size
        if h < w:
            new_h = target_size
            new_w = int(w * (target_size / h))
        else:
            new_w = target_size
            new_h = int(h * (target_size / w))
        
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        # Center crop to target_size x target_size
        h, w = img.shape[:2]
        start_y = (h - target_size) // 2
        start_x = (w - target_size) // 2
        img = img[start_y:start_y+target_size, start_x:start_x+target_size]
        
        # Normalize to [0, 1]
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)
        
        # 4. Prediction
        preds = model.predict(img, verbose=0)
        idx = np.argmax(preds)
        confidence = np.max(preds) * 100
        disease_name = class_names[idx]
        
        print(f"Prediction: {disease_name} ({confidence:.2f}%)")
        return disease_name, confidence
        
    except Exception as e:
        print(f"Error in predict function: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
