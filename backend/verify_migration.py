import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi
from bson.objectid import ObjectId

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Load environment variables
# .env is in the same directory as this script (backend/.env)
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

MONGO_URI = os.getenv('MONGO_URI')

def verify_migration():
    print("--- MongoDB Migration Verification ---")
    
    if not MONGO_URI:
        print("FAIL: MONGO_URI not found in environment.")
        return

    try:
        print(f"1. Connecting to MongoDB...")
        client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        db = client['crop_diagnosis_db']
        client.admin.command('ping')
        print("PASS: Connected successfully.")
        
        # Check Collections
        print("\n2. Verifying Collections and Data...")
        collections = db.list_collection_names()
        print(f"   Found collections: {collections}")
        
        # Check Diseases
        disease_count = db.diseases.count_documents({})
        if disease_count > 0:
            print(f"PASS: 'diseases' collection has {disease_count} records.")
        else:
            print("FAIL: 'diseases' collection is empty.")
            
        # Check Pesticides
        pesticide_count = db.pesticides.count_documents({})
        if pesticide_count > 0:
            print(f"PASS: 'pesticides' collection has {pesticide_count} records.")
        else:
            print("FAIL: 'pesticides' collection is empty.")
            
        # Check CRUD operations with a dummy user
        print("\n3. Testing Read/Write Operations (User Collection)...")
        users = db.users
        dummy_user = {
            "name": "Test User",
            "email": "test_migration_verify@example.com",
            "password_hash": "dummyhash123",
            "role": "tester"
        }
        
        # Insert
        result = users.insert_one(dummy_user)
        user_id = result.inserted_id
        print(f"   Inserted test user with ID: {user_id}")
        
        # Read
        fetched_user = users.find_one({"_id": user_id})
        if fetched_user and fetched_user['email'] == dummy_user['email']:
            print("PASS: Read operation successful.")
        else:
            print("FAIL: Read operation failed.")
            
        # Delete
        delete_result = users.delete_one({"_id": user_id})
        if delete_result.deleted_count == 1:
            print("PASS: Delete operation successful (Cleaned up test user).")
        else:
            print("FAIL: Delete operation failed.")
            
        print("\n--- Verification Completed Successfully! ---")
        
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_migration()
