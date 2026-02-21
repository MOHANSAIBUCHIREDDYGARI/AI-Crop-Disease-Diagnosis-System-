import tensorflow as tf
from tensorflow.keras.layers import Input, Lambda, Dense, Flatten
from tensorflow.keras.models import Model
from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
import numpy as np
from glob import glob
import matplotlib.pyplot as plt
import os

# --- Configuration ---
# Setting up our training parameters
IMAGE_SIZE = [224, 224] # VGG16 expects 224x224 images
BATCH_SIZE = 32
EPOCHS = 5
DATASET_PATH = os.path.join('dataset', 'Maize')
MODELS_DIR = 'models'

# Create the folder for saving models if it doesn't exist
if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR)

# --- Data Path Verification ---
print(f"Checking dataset at {DATASET_PATH}...")
if not os.path.exists(DATASET_PATH):
    print(f"Error: Dataset directory not found at {DATASET_PATH}")
    # Fallback check for alternate folder name
    if os.path.exists(os.path.join('dataset', 'Corn')):
        print("Found 'Corn' directory instead. Using that.")
        DATASET_PATH = os.path.join('dataset', 'Corn')
    else:
        exit(1)

# Find how many classes (folders) we have
folders = glob(os.path.join(DATASET_PATH, '*'))
print(f"Found {len(folders)} classes: {[os.path.basename(f) for f in folders]}")


# --- Model Architecture (Transfer Learning) ---
print("Loading VGG16 model...")
# We use VGG16, a powerful pre-trained model for image recognition
# include_top=False: We chop off the last part to add our own classifier
vgg = VGG16(input_shape=IMAGE_SIZE + [3], weights='imagenet', include_top=False)

# Freezing layers so we don't ruin the pre-learned features during training
for layer in vgg.layers:
    layer.trainable = False

# Add our custom layers
x = Flatten()(vgg.output)
# The final layer has as many neurons as we have crop diseases suitable for Maize for Maize
prediction = Dense(len(folders), activation='softmax')(x)

# Create the final model
model = Model(inputs=vgg.input, outputs=prediction)
model.summary()

# Tell the model how to learn
model.compile(
  loss='categorical_crossentropy',
  optimizer='adam',
  metrics=['accuracy']
)


# --- Data Preparation ---
print("Setting up Data Generators...")
# Data Augmentation: Randomly change images to help the model learn better
datagen = ImageDataGenerator(
    rescale=1./255,         # Normalize pixel values
    rotation_range=10,      # Small rotations
    width_shift_range=0.1,
    height_shift_range=0.1,
    shear_range=0.1,
    zoom_range=0.1,
    fill_mode='nearest',
    validation_split=0.2    # Keep 20% for testing
)

print("Loading Training Set...")
training_set = datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(224, 224),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training',      # Use the larger chunk for training
    shuffle=True
)

print("Loading Validation Set...")
validation_set = datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(224, 224),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation',    # Use the smaller chunk for validation
    shuffle=True
)

# --- Training ---
print(f"Starting training for {EPOCHS} epochs...")
history = model.fit(
  training_set,
  validation_data=validation_set,
  epochs=EPOCHS,
  steps_per_epoch=len(training_set),
  validation_steps=len(validation_set)
)

# --- Plotting Results ---
try:
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.plot(history.history['loss'], label='train loss')
    plt.plot(history.history['val_loss'], label='val loss')
    plt.legend()
    plt.title('Loss')

    plt.subplot(1, 2, 2)
    plt.plot(history.history['accuracy'], label='train acc')
    plt.plot(history.history['val_accuracy'], label='val acc')
    plt.legend()
    plt.title('Accuracy')
    
    plot_path = os.path.join(MODELS_DIR, 'maize_training_plot.png')
    plt.savefig(plot_path)
    print(f"Training plot saved to {plot_path}")
except Exception as e:
    print(f"Error plotting: {e}")


# --- Saving Model ---
model_name = 'maize_disease_model.h5'
model_path = os.path.join(MODELS_DIR, model_name)
model.save(model_path)
print(f"Model saved to {model_path}")
