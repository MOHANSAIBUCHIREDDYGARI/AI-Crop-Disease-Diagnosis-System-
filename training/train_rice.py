import tensorflow as tf
import os
import matplotlib.pyplot as plt
import numpy as np
from tensorflow.keras.applications import InceptionV3
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model

# --- Configuration ---
# Setting up the environment
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # Suppress unnecessary TensorFlow logs

print(f"TensorFlow Version: {tf.__version__}")

# Basic parameters
BATCH_SIZE = 32
EPOCHS = 30
IMAGE_SIZE = (299, 299) # InceptionV3 expects 299x299 images

DATASET_DIR = os.path.join('dataset', 'rice')
MODELS_DIR = 'models'

# Create the folder for saving models if it doesn't exist
if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR)

print(f"Checking dataset at {DATASET_DIR}...")

if not os.path.exists(DATASET_DIR):
    print(f"Error: Dataset directory not found in {DATASET_DIR}")
    exit(1)


# --- Data Preparation ---
print("Setting up Data Generators...")

# We use Data Augmentation to artificially increase our dataset
# This helps the model generalize better by seeing rotated, zoomed, and flipped versions of the images
train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
    rescale=1./255,         # Normalize pixel values
    rotation_range=40,      # Rotate images randomly
    horizontal_flip=True,   # Flip images horizontally
    width_shift_range=0.2,  # Shift width
    height_shift_range=0.2, # Shift height
    shear_range=0.2,        # Shear transformation
    zoom_range=0.2,         # Zoom in/out
    fill_mode='nearest',    # Fill empty pixels after transformation
    validation_split=0.2    # Use 20% of data for validation
)

# For validation, we only rescale (no random changes)
val_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2
)

print("Loading Training Data...")
train_generator = train_datagen.flow_from_directory(
    DATASET_DIR,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training', # This is the 80% used for training
    shuffle=True,
    seed=42 
)

print("Loading Validation Data...")
validation_generator = val_datagen.flow_from_directory(
    DATASET_DIR,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation', # This is the 20% used for checking progress
    shuffle=False,
    seed=42 
)

num_classes = train_generator.num_classes
print(f"Number of classes: {num_classes}")
print(f"Class indices: {train_generator.class_indices}")

# --- Model Architecture (Transfer Learning) ---
print("Building model with InceptionV3 (Keras Applications)...")
# We load a pre-trained model (InceptionV3) trained on ImageNet
# include_top=False means we remove the final classification layer so we can add our own
base_model = InceptionV3(weights='imagenet', include_top=False, input_shape=IMAGE_SIZE+(3,))

# Freezing the base model layers prevents them from being updated during the first phase of training
# We only want to train our custom layers at the end
base_model.trainable = False

# Add our custom layers on top
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(512, activation='relu')(x) # Add a dense layer for learning specific features
x = Dropout(0.2)(x)                  # Dropout helps prevent overfitting
predictions = Dense(num_classes, activation='softmax')(x) # Final output layer for our classes

# Combine base model and new layers
model = Model(inputs=base_model.input, outputs=predictions)

model.summary()

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), 
    loss='categorical_crossentropy',
    metrics=['accuracy'])

# --- Training ---
print(f"Starting training for {EPOCHS} epochs...")
history = model.fit(
        train_generator,
        steps_per_epoch=train_generator.samples // train_generator.batch_size,
        epochs=EPOCHS,
        validation_data=validation_generator,
        validation_steps=validation_generator.samples // validation_generator.batch_size,
        verbose=1
)

# --- Saving the Model ---
model_name = 'rice_disease_model.h5'
model_path = os.path.join(MODELS_DIR, model_name)
model.save(model_path)
print(f"Model saved to {model_path}")

# Plotting the results
try:
    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']
    loss = history.history['loss']
    val_loss = history.history['val_loss']
    epochs_range = range(len(acc))

    plt.figure(figsize=(8, 8))
    plt.subplot(1, 2, 1)
    plt.plot(epochs_range, acc, label='Training Accuracy')
    plt.plot(epochs_range, val_acc, label='Validation Accuracy')
    plt.legend(loc='lower right')
    plt.title('Training and Validation Accuracy')

    plt.subplot(1, 2, 2)
    plt.plot(epochs_range, loss, label='Training Loss')
    plt.plot(epochs_range, val_loss, label='Validation Loss')
    plt.legend(loc='upper right')
    plt.title('Training and Validation Loss')
    
    plot_path = os.path.join(MODELS_DIR, 'rice_training_plot.png')
    plt.savefig(plot_path)
    print(f"Training plot saved to {plot_path}")
except Exception as e:
    print(f"Error plotting: {e}")
