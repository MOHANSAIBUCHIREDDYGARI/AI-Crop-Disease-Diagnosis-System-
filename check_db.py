"""
Diagnostic Script
Used to manually check if diseases and pesticides are correctly linked in the database.
"""
import sqlite3
import os
import sys

# Connect to the database
db_path = 'database/crop_diagnosis.db'
if not os.path.exists(db_path):
    print(f"DB not found at {db_path}")
    sys.exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row # Allows accessing columns by name
cursor = conn.cursor()

def check_disease(crop, disease_name):
    print(f"\n--- Checking Disease: {disease_name} (Crop: {crop}) ---")
    
    # 1. Check if the disease exists in the main table
    rows = cursor.execute('SELECT * FROM diseases WHERE crop = ? AND disease_name = ?', (crop, disease_name)).fetchall()
    if rows:
        print(f"✅ Found in 'diseases' table: {[dict(r) for r in rows]}")
    else:
        print(f"❌ NOT found in 'diseases' table.")
        
    # ALWAYS show what IS there to help debug
    rows_partial = cursor.execute('SELECT disease_name FROM diseases WHERE crop = ?', (crop,)).fetchall()
    print(f"   Available diseases for {crop}: {[r['disease_name'] for r in rows_partial]}")

    # 2. Check if we have pesticides for this disease
    # We remove underscores to match the pesticide descriptions usually found in text
    disease_clean = disease_name.replace('___', ' ').replace('_', ' ')
    print(f"   Cleaning for pesticide search: '{disease_name}' -> '{disease_clean}'")
    
    query = "SELECT name, target_diseases FROM pesticides WHERE target_diseases LIKE ?"
    rows_pest = cursor.execute(query, (f'%{disease_clean}%',)).fetchall()
    
    if rows_pest:
        print(f"✅ Found matching pesticides: {[r['name'] for r in rows_pest]}")
    else:
        print(f"❌ NO pesticides found matching '%{disease_clean}%'")
        
        
        

# Test cases: Try finding Tomato Early Blight and Rice Brown Spot
# Test cases: Try finding specific diseases
check_disease('tomato', 'Target Spot')
check_disease('tomato', 'Healthy')

conn.close()
