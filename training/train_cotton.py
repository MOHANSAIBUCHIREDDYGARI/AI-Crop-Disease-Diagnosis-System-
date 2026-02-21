import tensorflow as tf
from tensorflow.keras.applications.resnet_v2 import ResNet152V2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models
import os
import matplotlib.pyplot as plt
import numpy as np

# --- Configuration ---
# Cotton model uses slightly larger images (300x300) for better detail
IMAGE_SIZE = (300, 300) 
BATCH_SIZE = 32
EPOCHS = 20
DATASET_DIR = os.path.join('dataset', 'cotton')
MODELS_DIR = 'models'

# Ensure the model directory exists
if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR)

# --- Data Verification ---
print(f"Checking dataset at {DATASET_DIR}...")
train_dir = os.path.join(DATASET_DIR, 'train')
val_dir = os.path.join(DATASET_DIR, 'val')

if not os.path.exists(train_dir) or not os.path.exists(val_dir):
    print(f"Error: Train/Val directories not found in {DATASET_DIR}")
    exit(1)


# --- Data Preparation ---
print("Setting up Data Generators...")
# Data Augmentation helps the model learn to recognize cotton diseases
# even if the photo is flipped or not perfectly aligned
datagen = ImageDataGenerator(
    rescale = 1./255,           # Convert pixel numbers to 0-1
    horizontal_flip = True,     # Flip sideways
    vertical_flip = True,       # Flip upside down
)

print("Loading Training Data...")
train_generator = datagen.flow_from_directory(
    train_dir,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    seed=88
)

print("Loading Validation Data...")
val_generator = datagen.flow_from_directory(
    val_dir,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    seed=88
)

num_classes = train_generator.num_classes
print(f"Number of classes: {num_classes}")
print(f"Class indices: {train_generator.class_indices}")


# --- Model Architecture (Transfer Learning) ---
print("Building ResNet152V2 Model...")
# We use ResNet152V2, a very deep and rigorous network
in_layer = layers.Input(shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 3))
resnet = ResNet152V2(include_top=False, weights='imagenet', input_tensor=in_layer)

# Freeze the ResNet layers so we don't accidentally wreck the pre-trained weights
for layer in resnet.layers:
    layer.trainable = False

# Add our custom classification head
x = layers.GlobalMaxPooling2D()(resnet.output)
x = layers.Flatten()(x)
output = layers.Dense(num_classes, activation='softmax')(x) # Final answer

model = models.Model(inputs=resnet.inputs, outputs=output)

# Learning Rate Scheduler: Slow down the learning as we get closer to the solution
initial_lr = 0.01
lr_scheduler = tf.keras.optimizers.schedules.ExponentialDecay(
    initial_lr,
    decay_steps=25,
    decay_rate=0.96,
    staircase=True
)

optim = tf.keras.optimizers.Adam(learning_rate=lr_scheduler)

model.compile(optimizer=optim, loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()


# --- Callbacks ---
# Stop early if we stop improving (saves time)
# AND save the best version of the model automatically
callbacks = [
    tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', mode='max', patience=10, verbose=1),
    tf.keras.callbacks.ModelCheckpoint(
        os.path.join(MODELS_DIR, 'cotton_best_model.h5'), 
        monitor='val_accuracy', 
        mode='max', 
        save_weights_only=False, 
        save_best_only=True,
        verbose=1
    )
]

# --- Training ---
print(f"Starting training for {EPOCHS} epochs...")
history = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    callbacks=callbacks,
    verbose=1
)

# --- Saving Final Model ---
model_name = 'cotton_disease_model.h5'
model_path = os.path.join(MODELS_DIR, model_name)
model.save(model_path)
print(f"Model saved to {model_path}")


# --- Plotting Results ---
try:
    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']
    loss = history.history['loss']
    val_loss = history.history['val_loss']
    epochs_range = range(len(acc))

    plt.figure(figsize=(12, 7))
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
    
    plot_path = os.path.join(MODELS_DIR, 'cotton_training_plot.png')
    plt.savefig(plot_path)
    print(f"Training plot saved to {plot_path}")
except Exception as e:
    print(f"Error plotting: {e}")
