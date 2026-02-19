import os
import json
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi

# Add the project root to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Load environment variables
# Load environment variables
# Path to .env file: C:\SE ROJECT\AI-Crop-Diagnosis\backend\.env
# Current file path: C:\SE ROJECT\AI-Crop-Diagnosis\backend\database\seed\mongo_seed.py
# We need to go up 3 levels to find backend/.env? No, wait. 
# backend/database/seed -> backend/database -> backend -> .env 
# So 3 levels of dirname
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

MONGO_URI = os.getenv('MONGO_URI')

if not MONGO_URI:
    # Try looking in the root folder just in case
    # backend/database/seed -> backend/database -> backend -> root
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env'))
    MONGO_URI = os.getenv('MONGO_URI')

if not MONGO_URI:
    print("Error: MONGO_URI not found in .env file or environment")
    sys.exit(1)

def seed_database():
    """Reads JSON files and populates MongoDB collections"""
    print(f"Connecting to MongoDB...")
    
    try:
        client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        db = client['crop_diagnosis_db']
        
        # Test connection
        client.admin.command('ping')
        print("Connected successfully!")
        
        # --- SEED DISEASES ---
        # The JSON files are in C:\SE ROJECT\AI-Crop-Diagnosis\database\seed
        # But this script is in C:\SE ROJECT\AI-Crop-Diagnosis\backend\database\seed
        # So we need to point to the correct location.
        # Actually, let's check where the user said the json files are.
        # list_dir showed they are in C:\SE ROJECT\AI-Crop-Diagnosis\database\seed
        # WAIT. I am writing this script to backend/database/seed/mongo_seed.py
        # So I need to go: backend/database/seed -> backend/database -> backend -> root -> database/seed
        
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        seed_data_dir = os.path.join(project_root, 'database', 'seed')
        
        diseases_path = os.path.join(seed_data_dir, 'diseases.json')
        if os.path.exists(diseases_path):
            with open(diseases_path, 'r', encoding='utf-8') as f:
                diseases_data = json.load(f)
            
            if diseases_data:
                collection = db['diseases']
                # Clear existing data to avoid duplicates/conflicts during development
                print(f"Clearing existing {collection.name}...")
                collection.delete_many({})
                
                print(f"Seeding {len(diseases_data)} diseases...")
                collection.insert_many(diseases_data)
                print("Diseases seeded successfully!")
            else:
                print("No data found in diseases.json")
        else:
            print(f"Warning: diseases.json not found at {diseases_path}")

        # --- SEED PESTICIDES ---
        pesticides_path = os.path.join(seed_data_dir, 'pesticides.json')
        if os.path.exists(pesticides_path):
            with open(pesticides_path, 'r', encoding='utf-8') as f:
                pesticides_data = json.load(f)
            
            if pesticides_data:
                collection = db['pesticides']
                # Clear existing
                print(f"\nClearing existing {collection.name}...")
                collection.delete_many({})
                
                print(f"Seeding {len(pesticides_data)} pesticides...")
                collection.insert_many(pesticides_data)
                print("Pesticides seeded successfully!")
            else:
                print("No data found in pesticides.json")
        else:
            print(f"Warning: pesticides.json not found at {pesticides_path}")

        print("\nDatabase seeding completed!")

    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    seed_database()
