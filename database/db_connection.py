import os
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', '.env'))

class Database:
    """
    MongoDB Database Connection Wrapper
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the MongoDB connection"""
        self.mongo_uri = os.getenv('MONGO_URI')
        if not self.mongo_uri:
            # Fallback for when .env isn't loaded correctly or simple test runs
            print("WARNING: MONGO_URI not found in env, using default local or checking backend .env")
            pass
            
        try:
            # Connect to MongoDB Atlas
            # tlsCAFile is needed for secure connections on some networks
            if self.mongo_uri:
                self.client = MongoClient(self.mongo_uri, tlsCAFile=certifi.where())
            else:
                raise ValueError("MONGO_URI not set")

            # The database name is usually part of the URI or we pick a default
            self.db = self.client['crop_diagnosis_db']
            
            # Ping to check if connection is successful
            self.client.admin.command('ping')
            print("Implementation: Successfully connected to MongoDB!")
            
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            raise e

    def get_collection(self, collection_name):
        """Get a specific collection (like a table in SQL)"""
        return self.db[collection_name]

# Create a global instance
db = Database()
