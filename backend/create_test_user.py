import os
import sys
import bcrypt
import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi

# Add path to find modules if needed, though we will likely run this from backend dir
sys.path.append(os.path.dirname(__file__))

# Load env
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
MONGO_URI = os.getenv('MONGO_URI')

if not MONGO_URI:
    print("Error: MONGO_URI not found")
    sys.exit(1)

def create_test_user():
    try:
        print("Connecting to MongoDB...")
        client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        db = client['crop_diagnosis_db']
        users_collection = db.users
        
        # List existing users
        print("\nExisting Users:")
        users = list(users_collection.find({}, {'email': 1, '_id': 0}))
        if users:
            for u in users:
                print(f" - {u['email']}")
        else:
            print(" - None")
            
        # Create test user
        email = "test@example.com"
        password = "password123"
        
        if users_collection.find_one({'email': email}):
            print(f"\nUser {email} already exists. Updating password...")
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            users_collection.update_one(
                {'email': email},
                {'$set': {'password_hash': password_hash}}
            )
            print(f"Password for {email} reset to '{password}'")
        else:
            print(f"\nCreating new user {email}...")
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            new_user = {
                'email': email,
                'password_hash': password_hash,
                'name': "Test User",
                'preferred_language': 'en',
                'created_at': datetime.datetime.utcnow(),
                'updated_at': datetime.datetime.utcnow()
            }
            users_collection.insert_one(new_user)
            print(f"User {email} created with password '{password}'")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_test_user()
