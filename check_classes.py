import os

dataset_root = 'dataset'
crops = ['Grape', 'Maize', 'Potato', 'rice', 'tomato']

for crop in crops:
    path = os.path.join(dataset_root, crop)
    if not os.path.exists(path):
        print(f"MISSING: {crop}")
        continue
    
    
    subdirs = os.listdir(path)
    train_dir = next((d for d in subdirs if d.lower() == 'train'), None)
    
    if train_dir:
        path = os.path.join(path, train_dir)
        subdirs = os.listdir(path)
    
    
    classes = [d for d in subdirs if os.path.isdir(os.path.join(path, d))]
    classes.sort()
    
    print(f"\n--- {crop} Classes (Sorted) ---")
    for i, c in enumerate(classes):
        print(f"{i}: {c}")
