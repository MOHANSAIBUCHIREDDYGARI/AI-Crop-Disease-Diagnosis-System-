import shutil
import os
import sys

def cleanup():
    sites = [
        r"C:\Users\mohansai\AppData\Local\Programs\Python\Python310\lib\site-packages",
        r"C:\Users\mohansai\AppData\Roaming\Python\Python310\site-packages"
    ]
    
    targets = ["google", "protobuf"]
    
    for site in sites:
        if not os.path.exists(site):
            continue
        print(f"Checking site: {site}")
        for folder in os.listdir(site):
            lower_folder = folder.lower()
            if any(t in lower_folder for t in targets) or folder.startswith("~"):
                full_path = os.path.join(site, folder)
                print(f"Deleting: {full_path}")
                try:
                    if os.path.isdir(full_path):
                        shutil.rmtree(full_path)
                    else:
                        os.remove(full_path)
                except Exception as e:
                    print(f"Failed to delete {folder}: {e}")

if __name__ == "__main__":
    cleanup()
