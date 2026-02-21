import os
import argparse
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model

# basic settings
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 5

# Parse command line argument to know which crop we are training for
parser = argparse.ArgumentParser()
parser.add_argument("--crop", required=True)
args = parser.parse_args()

# Setup paths dynamically based on the crop name
TRAIN_DIR = f"dataset/{args.crop}/train"
VAL_DIR = f"dataset/{args.crop}/val"
MODEL_PATH = f"models/{args.crop}_disease_model.h5"

# Helper function to find all disease classes (folders)
def get_classes(path):
    return sorted([
        d for d in os.listdir(path)
        if os.path.isdir(os.path.join(path, d))
    ])

CLASSES = get_classes(TRAIN_DIR)

# --- Data Preparation ---
# Create a data generator that will load images and apply random transformations
# This helps the model learn to recognize diseases even in imperfect photos
train_gen = ImageDataGenerator(
    rescale=1./255,         # Normalize pixel values
    rotation_range=20,      # Rotate images slightly
    zoom_range=0.2,         # Zoom inside the image
    horizontal_flip=True    # Flip horizontally
)

# For validation, we only normalize, no random changes
val_gen = ImageDataGenerator(rescale=1./255)

# Load the actual images from the folders
train_data = train_gen.flow_from_directory(
    TRAIN_DIR,
    classes=CLASSES,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode="categorical"
)

val_data = val_gen.flow_from_directory(
    VAL_DIR,
    classes=CLASSES,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode="categorical"
)

# --- Model Building ---
# We use MobileNetV2, which is lightweight and fast (good for mobile apps)
base = MobileNetV2(
    weights="imagenet",
    include_top=False, # Remove the final layer so we can add our own
    input_shape=(IMG_SIZE, IMG_SIZE, 3)
)
# Freeze the base model so we don't destroy pre-learned weights
base.trainable = False

# Add our custom layers
x = GlobalAveragePooling2D()(base.output)
x = Dropout(0.3)(x) # Dropout helps prevent overfitting
output = Dense(len(CLASSES), activation="softmax")(x) # Final classification layer

# Create the model
model = Model(base.input, output)
model.compile(optimizer="adam",
              loss="categorical_crossentropy",
              metrics=["accuracy"])

# --- Training ---
print(f"Starting training for {args.crop}...")
model.fit(train_data, validation_data=val_data, epochs=EPOCHS)

# --- Save ---
model.save(MODEL_PATH)
print(f"✅ Model saved at {MODEL_PATH}")
