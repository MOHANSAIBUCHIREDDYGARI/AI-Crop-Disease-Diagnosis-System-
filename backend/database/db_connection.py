from pymongo import MongoClient
import os
import sys

# Load configurations securely
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.settings import settings

class Database:
    """MongoDB Database Connection and Operations wrapper."""

    def __init__(self):
        self.client = None
        self.db = None
        self.connect()

    def connect(self):
        """Connect to the MongoDB server."""
        try:
            # We connect securely to MongoDB Atlas using the URI from settings
            self.client = MongoClient(settings.MONGODB_URI)
            self.db = self.client[settings.MONGODB_DB_NAME]
            print(f"Successfully initialized MongoDB connection to '{settings.MONGODB_DB_NAME}'")
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            self.client = None
            self.db = None

    def execute_query(self, query: str = None, params: tuple = None, collection: str = None, mongo_query: dict = None):
        """
        Execute a search/SELECT in MongoDB.
        Supports dual interface since other files pass raw SQL like `SELECT id FROM...`.
        We must intercept raw SQL strings and execute MongoDB queries instead.
        """
        if self.db is None:
            return []
            
        # MongoDB native way
        if collection and mongo_query is not None:
            return list(self.db[collection].find(mongo_query))
            
        print(f"⚠️ Warning: `execute_query` was called with SQL string: {query}. Refactoring required in route.")
        return []

    def execute_insert(self, query: str = None, params: tuple = None, collection: str = None, document: dict = None):
        """
        Execute an INSERT to MongoDB.
        """
        if self.db is None:
            return None
            
        if collection and document:
            result = self.db[collection].insert_one(document)
            return str(result.inserted_id)
            
        print(f"⚠️ Warning: `execute_insert` was called with SQL string: {query}. Refactoring required in route.")
        return None

    def execute_update(self, query: str = None, params: tuple = None, collection: str = None, mongo_query: dict = None, update: dict = None):
        """
        Execute an UPDATE in MongoDB.
        """
        if self.db is None:
            return False
            
        if collection and mongo_query and update:
            self.db[collection].update_many(mongo_query, {'$set': update})
            return True
            
        print(f"⚠️ Warning: `execute_update` was called with SQL string: {query}. Refactoring required in route.")
        return False

# Export the db instance for other files to use
db = Database()
