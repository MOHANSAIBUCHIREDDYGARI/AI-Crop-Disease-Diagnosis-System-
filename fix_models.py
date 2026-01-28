import h5py
import json
import os

def fix_model_config(model_path):
    print(f"Attempting to fix config for {model_path}...")
    try:
        with h5py.File(model_path, 'r+') as f:
            if 'model_config' in f.attrs:
                config_raw = f.attrs['model_config']
                if isinstance(config_raw, bytes):
                    config_raw = config_raw.decode('utf-8')
                config = json.loads(config_raw)
                
                # Recursively remove batch_shape and dtype_policy
                def clean_config(obj):
                    if isinstance(obj, dict):
                        obj.pop('batch_shape', None)
                        obj.pop('dtype_policy', None)
                        obj.pop('DTypePolicy', None)
                        for k, v in obj.items():
                            clean_config(v)
                    elif isinstance(obj, list):
                        for item in obj:
                            clean_config(item)

                clean_config(config)
                f.attrs['model_config'] = json.dumps(config).encode('utf-8')
                print(f"Successfully cleaned config for {model_path}")
            else:
                print(f"No model_config found in {model_path}")
    except Exception as e:
        print(f"Failed to fix {model_path}: {str(e)}")

models_dir = 'd:/SE ROJECT/AI-Crop-Diagnosis/models'
for model_file in os.listdir(models_dir):
    if model_file.endswith('.h5'):
        fix_model_config(os.path.join(models_dir, model_file))
