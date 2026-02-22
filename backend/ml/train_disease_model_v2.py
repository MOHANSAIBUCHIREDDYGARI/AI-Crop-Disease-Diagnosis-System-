"""
FAST Disease Classification Model Training Script
Optimized for CPU / low-end GPU
Uses MobileNetV2 for faster training
"""

import os
import argparse
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam


# --- Configuration ---
IMG_SIZE = 224
BATCH_SIZE = 16 # Smaller batch size for lower memory usage
EPOCHS = 15
INITIAL_LR = 0.0005


# Command line arguments to make the script flexible for different crops
parser = argparse.ArgumentParser(description="Train disease classification model")
parser.add_argument("--crop", required=True, help="Crop type (tomato, cotton)")
parser.add_argument("--epochs", type=int, default=EPOCHS)
parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
parser.add_argument("--lr", type=float, default=INITIAL_LR)
args = parser.parse_args()


# --- Paths ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TRAIN_DIR = os.path.join(PROJECT_ROOT, f"dataset/{args.crop}/train")
VAL_DIR = os.path.join(PROJECT_ROOT, f"dataset/{args.crop}/val")
MODEL_PATH = os.path.join(PROJECT_ROOT, f"models/{args.crop}_disease_model.h5")
CHECKPOINT_PATH = os.path.join(PROJECT_ROOT, f"models/{args.crop}_best_model.h5")

os.makedirs(os.path.join(PROJECT_ROOT, "models"), exist_ok=True)


# --- Helpers ---
def get_classes(path):
    # Find all subdirectories (which represent classes)
    return sorted([d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))])

CLASSES = get_classes(TRAIN_DIR)
NUM_CLASSES = len(CLASSES)

print(f"\nCrop: {args.crop}")
print(f"Classes ({NUM_CLASSES}): {CLASSES}")
print(f"Epochs: {args.epochs}, Batch size: {args.batch_size}\n")


# --- Data Preparation ---
# Data augmentation to make the model robust
train_gen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=15,
    zoom_range=0.1,
    horizontal_flip=True
)

val_gen = ImageDataGenerator(rescale=1./255)

print("Loading training data...")
train_data = train_gen.flow_from_directory(
    TRAIN_DIR,
    classes=CLASSES,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=args.batch_size,
    class_mode="categorical",
    shuffle=True
)

print("Loading validation data...")
val_data = val_gen.flow_from_directory(
    VAL_DIR,
    classes=CLASSES,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=args.batch_size,
    class_mode="categorical",
    shuffle=False
)


# --- Model Architecture ---
print("Building MobileNetV2 model...")

# Load MobileNetV2 without the top layer (transfer learning)
base_model = MobileNetV2(
    weights="imagenet",
    include_top=False,
    input_shape=(IMG_SIZE, IMG_SIZE, 3)
)

# Freeze base model layers so they don't change
base_model.trainable = False

# Add custom classification head
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dropout(0.3)(x)
output = Dense(NUM_CLASSES, activation="softmax")(x)

model = Model(inputs=base_model.input, outputs=output)

model.compile(
    optimizer=Adam(learning_rate=args.lr),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

print(f"Total parameters: {model.count_params():,}\n")


# --- Callbacks ---
# These help us train better and save the best results
callbacks = [
    # Reduce learning rate if we get stuck
    ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, verbose=1),
    # Stop early if we stop improving
    EarlyStopping(monitor="val_loss", patience=4, restore_best_weights=True, verbose=1),
    # Save the best model found during training
    ModelCheckpoint(CHECKPOINT_PATH, monitor="val_accuracy", save_best_only=True, verbose=1)
]


# --- Training ---
print("Starting training...\n")

history = model.fit(
    train_data,
    validation_data=val_data,
    epochs=args.epochs,
    callbacks=callbacks,
    verbose=1
)


# --- Save Final Model ---
model.save(MODEL_PATH)

print("\nTraining completed!")
print(f"Final model saved at: {MODEL_PATH}")
print(f"Best model saved at: {CHECKPOINT_PATH}")


print("\nFinal Metrics:")
print(f"Training Accuracy: {history.history['accuracy'][-1]:.4f}")
print(f"Validation Accuracy: {history.history['val_accuracy'][-1]:.4f}")
