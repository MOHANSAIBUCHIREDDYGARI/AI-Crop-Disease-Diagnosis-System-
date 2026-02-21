import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Activation
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os
import matplotlib.pyplot as plt

# --- Configuration ---
# Defining how big our images should be and how long to train
IMAGE_SIZE = (256, 256)
BATCH_SIZE = 32
EPOCHS = 10
DATASET_DIR = os.path.join('dataset', 'Grape')
MODELS_DIR = 'models'

# Make sure we have a place to save our work
if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR)

# --- Data Check ---
print(f"Checking dataset at {DATASET_DIR}...")
train_dir = os.path.join(DATASET_DIR, 'train')
test_dir = os.path.join(DATASET_DIR, 'test')

if not os.path.exists(train_dir):
    print(f"Error: Train directory not found in {DATASET_DIR}")
    exit(1)


# --- Data Preparation ---
print("Setting up Data Generators (Grayscale)...")
# Note: Usually colored images are better, but we'll try grayscale here if that's what was intended
# or just a choice for this specific model architecture
train_datagen = ImageDataGenerator(
    rescale=1./255,   # Normalize pixel values
    validation_split=0.15 
)

print("Loading Training Data...")
# We use color_mode='grayscale' so the input shape will be (256, 256, 1) instead of 3 channels
train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    color_mode='grayscale', 
    class_mode='categorical',
    subset='training',
    shuffle=True
)

print("Loading Validation Data...")
validation_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    color_mode='grayscale',
    class_mode='categorical',
    subset='validation',
    shuffle=True
)

num_classes = train_generator.num_classes
print(f"Number of classes: {num_classes}")
print(f"Class indices: {train_generator.class_indices}")


# --- Model Architecture ---
print("Building Custom CNN Model...")
model = Sequential()

# 1st Convolutional Layer
# Extract low-level features like edges
model.add(layers.Conv2D(32, (3,3), padding='same', input_shape=(256, 256, 1), activation='relu'))
model.add(layers.Conv2D(64, (3,3), activation='relu')) 

# Max Pooling reduces the size of the image representation
model.add(layers.MaxPool2D(pool_size=(8,8)))

# 2nd Convolutional Layer
# Extract higher-level features (shapes, textures)
model.add(layers.Conv2D(32, (3,3), padding='same', activation='relu'))
model.add(layers.Conv2D(64, (3,3), activation='relu'))

model.add(layers.MaxPool2D(pool_size=(8,8)))

model.add(Activation('relu'))

# Final Classification Layers
model.add(layers.Flatten())
model.add(layers.Dense(256, activation='relu'))
model.add(layers.Dense(num_classes, activation='softmax')) # Output layer

model.summary()

# Configure the training process
model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])

# --- Training ---
print(f"Starting training for {EPOCHS} epochs...")
history = model.fit(
    train_generator,
    epochs=EPOCHS,
    validation_data=validation_generator,
    verbose=1
)

# --- Saving ---
model_name = 'grape_disease_model.h5'
model_path = os.path.join(MODELS_DIR, model_name)
model.save(model_path)
print(f"Model saved to {model_path}")


# --- Evaluation ---
if os.path.exists(test_dir):
    print("Evaluating on Test Data...")
    test_datagen = ImageDataGenerator(rescale=1./255)
    test_generator = test_datagen.flow_from_directory(
        test_dir,
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        color_mode='grayscale', # Match training mode
        class_mode='categorical',
        shuffle=False
    )
    scores = model.evaluate(test_generator)
    print(f"Test Accuracy: {scores[1]*100:.2f}%")


# --- Plotting ---
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
    
    plot_path = os.path.join(MODELS_DIR, 'grape_training_plot.png')
    plt.savefig(plot_path)
    print(f"Training plot saved to {plot_path}")
except Exception as e:
    print(f"Error plotting: {e}")
