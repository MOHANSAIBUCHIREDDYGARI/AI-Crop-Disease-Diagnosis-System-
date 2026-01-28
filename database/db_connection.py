import sqlite3
import os
from contextlib import contextmanager
from typing import Optional

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), 'crop_diagnosis.db')

class Database:
    """SQLite database connection manager"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database and create tables if they don't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
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
            
            # Diagnosis history table
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
            
            # Pesticide recommendations table (linked to diagnosis)
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
            
            # Cost calculations table
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
            
            # Chatbot conversations table
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
            
            # Disease information table (seed data)
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
            
            # Pesticides master table (seed data)
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
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = ()):
        """Execute a query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute an insert query and return the last row id"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.lastrowid
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an update/delete query and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount

# Global database instance
db = Database()
