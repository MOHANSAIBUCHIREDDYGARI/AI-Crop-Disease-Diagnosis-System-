import tensorflow as tf
from tensorflow.keras import models, layers
import tensorflow_model_optimization as tfmot
import matplotlib.pyplot as plt
import os
import numpy as np

# --- Configuration ---
# Setting up basic parameters for our model
IMAGE_SIZE = 256    # We'll resize all images to 256x256
BATCH_SIZE = 32     # Process 32 images at a time
EPOCHS = 10         # How many times to go through the entire dataset
MODELS_DIR = 'models'
DATASET_DIR = os.path.join('dataset', 'tomato')

# Create the folder for saving models if it doesn't exist
if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR)

print(f"Checking dataset at {DATASET_DIR}...")
train_dir = os.path.join(DATASET_DIR, 'train')
val_dir = os.path.join(DATASET_DIR, 'val')

if not os.path.exists(train_dir) or not os.path.exists(val_dir):
    print(f"Error: Train/Val directories not found in {DATASET_DIR}")
    # We can't train without data!
    exit(1)


# --- Data Loading ---
print("Loading Training/Validation Data...")
# Load training data from the folder
train_ds = tf.keras.preprocessing.image_dataset_from_directory(
    train_dir,
    shuffle=True,
    image_size=(IMAGE_SIZE, IMAGE_SIZE),
    batch_size=BATCH_SIZE
)

# Load validation data (to test how well we're doing while training)
val_ds = tf.keras.preprocessing.image_dataset_from_directory(
    val_dir,
    shuffle=True,
    image_size=(IMAGE_SIZE, IMAGE_SIZE),
    batch_size=BATCH_SIZE
)

class_names = train_ds.class_names
n_classes = len(class_names)
print(f"Classes ({n_classes}): {class_names}")

# Optimize data loading for performance
AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

# --- Preprocessing Layers ---
# Resize images and scale pixel values to 0-1 range
resize_and_rescale = tf.keras.Sequential([
  layers.Resizing(IMAGE_SIZE, IMAGE_SIZE),
  layers.Rescaling(1./255),
])

# Add some randomness to training images to make the model robust (Data Augmentation)
data_augmentation = tf.keras.Sequential([
  layers.RandomFlip("horizontal_and_vertical"),
  layers.RandomRotation(0.2),
])

input_shape = (BATCH_SIZE, IMAGE_SIZE, IMAGE_SIZE, 3)

# --- Model Architecture ---
print("Building CNN Model...")
model = models.Sequential([
    resize_and_rescale,
    data_augmentation,
    # Convolutional layers to learn features (edges, textures, shapes)
    layers.Conv2D(32, kernel_size=(3,3), activation='relu', input_shape=(IMAGE_SIZE, IMAGE_SIZE, 3)),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64,  kernel_size=(3,3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64,  kernel_size=(3,3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Flatten(),
    layers.Dense(64, activation='relu'),
    layers.Dense(n_classes, activation='softmax'), # Final output layer
])

model.build(input_shape=input_shape)
model.summary()

model.compile(
    optimizer='adam',
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
    metrics=['accuracy']
)

# --- Training ---
print(f"Starting training for {EPOCHS} epochs...")
history = model.fit(
    train_ds,
    batch_size=BATCH_SIZE,
    validation_data=val_ds,
    epochs=EPOCHS,
    verbose=1
)

# --- Saving the Model ---
model_name = 'tomato_disease_model.h5'
model_path = os.path.join(MODELS_DIR, model_name)
model.save(model_path)
print(f"Model saved to {model_path}")

# Plot accuracy and loss graphs
try:
    plt.figure(figsize=(8, 8))
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Training Accuracy')
    plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
    plt.legend(loc='lower right')
    plt.title('Training and Validation Accuracy')

    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.legend(loc='upper right')
    plt.title('Training and Validation Loss')
    plot_path = os.path.join(MODELS_DIR, 'tomato_training_plot.png')
    plt.savefig(plot_path)
    print(f"Training plot saved to {plot_path}")
except Exception as e:
    print(f"Error plotting: {e}")


# --- Optimization (QAT & TFLite) ---
print("\n--- Starting Quantization Aware Training ---")

try:
    # Make the model smaller and faster for mobile use
    quant_aware_model = tfmot.quantization.keras.quantize_model(model)
    quant_aware_model.summary()

    quant_aware_model.compile(
        optimizer='adam',
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
        metrics=['accuracy']
    )

    print("Fine-tuning with QAT for 2 epochs...")
    q_history = quant_aware_model.fit(
        train_ds,
        batch_size=BATCH_SIZE,
        validation_data=val_ds,
        epochs=2,
        verbose=1
    )
except Exception as e:
    print(f"Error during QAT setup/training: {e}")
    # Fallback to original model if QAT fails
    quant_aware_model = model


print("\n--- Converting to TFLite ---")
converter = tf.lite.TFLiteConverter.from_keras_model(quant_aware_model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]

try:
    quantized_tflite_model = converter.convert()
    tflite_path = os.path.join(MODELS_DIR, 'tomato_disease_model.tflite')
    with open(tflite_path, 'wb') as f:
        f.write(quantized_tflite_model)
    print(f"Quantized TFLite model saved to {tflite_path}")
except Exception as e:
    print(f"Error converting to TFLite: {e}")

print("Done.")
