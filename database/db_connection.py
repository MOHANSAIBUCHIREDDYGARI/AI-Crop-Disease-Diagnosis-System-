import sqlite3
import os
from contextlib import contextmanager
from typing import Optional


# This is where our actual database file lives on the hard drive
DB_PATH = os.path.join(os.path.dirname(__file__), 'crop_diagnosis.db')

class Database:
    """
    The Librarian for our data.
    It handles opening the book (database), writing notes (saving data), and reading them back.
    """
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """
        Setup the library shelves (Tables) if they don't exist yet.
        This runs every time the app starts, just to be safe.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Table 1: Users
            # Stores who is using the app (names, login info, farm details)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    name TEXT NOT NULL,
                    phone TEXT,
                    farm_location TEXT,
                    farm_size REAL,
                    preferred_language TEXT DEFAULT 'en',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table 2: Diagnosis History
            # Records every time a user uploads a photo for a checkup
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS diagnosis_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    crop TEXT NOT NULL,
                    disease TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    severity_percent REAL NOT NULL,
                    stage TEXT NOT NULL,
                    image_path TEXT,
                    latitude REAL,
                    longitude REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            
            # Table 3: Pesticide Recommendations
            # Remembers what medicines we told the user to buy
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pesticide_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    diagnosis_id INTEGER NOT NULL,
                    pesticide_name TEXT NOT NULL,
                    dosage TEXT NOT NULL,
                    frequency TEXT NOT NULL,
                    cost_per_unit REAL NOT NULL,
                    is_organic BOOLEAN DEFAULT 0,
                    warnings TEXT,
                    FOREIGN KEY (diagnosis_id) REFERENCES diagnosis_history(id) ON DELETE CASCADE
                )
            ''')
            
            # Table 4: Cost Calculations
            # Stores the estimated bill for the treatment
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cost_calculations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    diagnosis_id INTEGER NOT NULL,
                    land_area REAL NOT NULL,
                    treatment_cost REAL NOT NULL,
                    prevention_cost REAL NOT NULL,
                    total_cost REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (diagnosis_id) REFERENCES diagnosis_history(id) ON DELETE CASCADE
                )
            ''')
            
            # Table 5: Chatbot History
            # Keeps a record of conversations with the AI Assistant
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chatbot_conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    response TEXT NOT NULL,
                    language TEXT DEFAULT 'en',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            
            # Table 6: Diseases Knowledge Base
            # Static info about various crop diseases
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS diseases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    crop TEXT NOT NULL,
                    disease_name TEXT NOT NULL,
                    description TEXT,
                    symptoms TEXT,
                    prevention_steps TEXT,
                    is_healthy BOOLEAN DEFAULT 0,
                    UNIQUE(crop, disease_name)
                )
            ''')
            
            # Table 7: Pesticides Inventory
            # List of all available medicines and their details
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pesticides (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    type TEXT NOT NULL,
                    target_diseases TEXT,
                    dosage_per_acre TEXT,
                    frequency TEXT,
                    cost_per_liter REAL,
                    is_organic BOOLEAN DEFAULT 0,
                    is_government_approved BOOLEAN DEFAULT 1,
                    warnings TEXT,
                    incompatible_with TEXT
                )
            ''')
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """
        A helper to easily open and close the door (connection).
        It makes sure the door is always closed processing is done, even if there's an error.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Let us access columns by name (row['email']) instead of index (row[1])
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback() # Undo changes if something went wrong
            raise e
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = ()):
        """Read data from the database (SELECT)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Add new data and return the ID of the new row"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.lastrowid
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Modify existing data (UPDATE or DELETE)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount


db = Database()
