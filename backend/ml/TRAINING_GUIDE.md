# Model Training Guide

## Quick Start

### Train with Improved Script (Recommended)

```bash
cd backend/ml
python train_disease_model_v2.py --crop tomato
```

### Training Options

```bash
# Custom epochs
python train_disease_model_v2.py --crop tomato --epochs 50

# Custom batch size
python train_disease_model_v2.py --crop tomato --batch-size 16

# Custom learning rate
python train_disease_model_v2.py --crop tomato --lr 0.0001

# All options
python train_disease_model_v2.py --crop tomato --epochs 50 --batch-size 16 --lr 0.0001
```

## Features

### ✅ EfficientNetB0 Architecture
- State-of-the-art accuracy/efficiency ratio
- Better than MobileNetV2 (3-5% accuracy improvement)
- Pre-trained on ImageNet

### ✅ Advanced Data Augmentation
- Rotation (±30°)
- Width/height shift (20%)
- Zoom (20%)
- Horizontal/vertical flip
- Brightness adjustment
- Shear transformation

### ✅ Training Optimizations
- **Learning Rate Scheduling**: Reduces LR when validation loss plateaus
- **Early Stopping**: Stops training when no improvement (patience=5)
- **Model Checkpointing**: Saves best model based on validation accuracy
- **Mixed Precision**: Faster training on modern GPUs

### ✅ Monitoring
- **TensorBoard**: Real-time training visualization
- **Metrics**: Accuracy, Precision, Recall
- **Logs**: Saved in `logs/` directory

## View Training Progress

```bash
tensorboard --logdir=logs/tomato
```

Then open http://localhost:6006 in your browser

## Dataset Structure

```
dataset/
├── tomato/
│   ├── train/
│   │   ├── Healthy/
│   │   ├── Tomato___Bacterial_spot/
│   │   └── ...
│   └── val/
│       ├── Healthy/
│       ├── Tomato___Bacterial_spot/
│       └── ...
```

## Output Files

- `models/{crop}_disease_model.h5` - Final trained model
- `models/checkpoints/{crop}_best_model.h5` - Best model during training
- `logs/{crop}/` - TensorBoard logs

## Backward Compatibility

The updated `disease_classifier.py` automatically detects whether a model is:
- **EfficientNetB0** (new, better accuracy)
- **MobileNetV2** (old, still supported)

No changes needed to existing code!

## Training Tips

1. **GPU Recommended**: Training is 10-20x faster on GPU
2. **Batch Size**: Reduce if you get out-of-memory errors
3. **Epochs**: 20-30 usually sufficient with early stopping
4. **Validation Data**: Ensure 20% of data is in `val/` folder

## Expected Training Time

| Hardware | Batch Size | Time per Epoch |
|----------|-----------|----------------|
| GPU (RTX 3060) | 32 | ~2-3 minutes |
| GPU (GTX 1660) | 32 | ~4-5 minutes |
| CPU | 32 | ~30-40 minutes |

## Troubleshooting

**Out of Memory?**
```bash
python train_disease_model_v2.py --crop tomato --batch-size 16
```

**Training too slow?**
- Use GPU if available
- Reduce batch size
- Reduce epochs

**Low accuracy?**
- Ensure good quality training data
- Check data augmentation settings
- Increase epochs
- Try different learning rates
