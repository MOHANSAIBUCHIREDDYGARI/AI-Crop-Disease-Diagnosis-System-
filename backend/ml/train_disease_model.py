import os
import argparse
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model

IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 5

parser = argparse.ArgumentParser()
parser.add_argument("--crop", required=True)
args = parser.parse_args()

TRAIN_DIR = f"dataset/{args.crop}/train"
VAL_DIR = f"dataset/{args.crop}/val"
MODEL_PATH = f"models/{args.crop}_disease_model.h5"

def get_classes(path):
    return sorted([
        d for d in os.listdir(path)
        if os.path.isdir(os.path.join(path, d))
    ])

CLASSES = get_classes(TRAIN_DIR)

train_gen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    zoom_range=0.2,
    horizontal_flip=True
)

val_gen = ImageDataGenerator(rescale=1./255)

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

base = MobileNetV2(
    weights="imagenet",
    include_top=False,
    input_shape=(IMG_SIZE, IMG_SIZE, 3)
)
base.trainable = False

x = GlobalAveragePooling2D()(base.output)
x = Dropout(0.3)(x)
output = Dense(len(CLASSES), activation="softmax")(x)

model = Model(base.input, output)
model.compile(optimizer="adam",
              loss="categorical_crossentropy",
              metrics=["accuracy"])

model.fit(train_data, validation_data=val_data, epochs=EPOCHS)
model.save(MODEL_PATH)

print(f"✅ Model saved at {MODEL_PATH}")
