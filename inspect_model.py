import h5py
import json
import os

models_dir = 'd:/SE ROJECT/AI-Crop-Diagnosis/models'

for filename in os.listdir(models_dir):
    if not filename.endswith('.h5'):
        continue
        
    model_path = os.path.join(models_dir, filename)
    print(f"\n{'='*20}\nInspecting: {filename}\n{'='*20}")

    try:
        with h5py.File(model_path, 'r') as f:
            if 'model_config' in f.attrs:
                config_str = f.attrs['model_config']
                if isinstance(config_str, bytes):
                    config_str = config_str.decode('utf-8')
                conf = json.loads(config_str)
                
                print("Model Type:", conf.get('class_name'))
                
                
                layers = conf['config']['layers']
                print("First 3 layers:")
                for layer in layers[:3]:
                    print(f" - {layer['class_name']}: {layer['config']['name']}")
                    
                
                is_mobilenet = any('expanded_conv' in l['config']['name'] for l in layers)
                print(f"Contains 'expanded_conv' layers (MobileNetV2 check): {is_mobilenet}")
                    
    except Exception as e:
        print("Error reading model:", e)
