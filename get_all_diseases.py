import sqlite3
import os

# Adjust path if needed, assuming running from root
db_path = 'database/crop_diagnosis.db'
if not os.path.exists(db_path):
    # Try backend/database/crop_diagnosis.db just in case
    db_path = 'backend/database/crop_diagnosis.db'

print(f"Connecting to {db_path}...")
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    crops = cursor.execute('SELECT DISTINCT crop FROM diseases').fetchall()
    print("Crops found:", [c[0] for c in crops])
    
    for crop in crops:
        crop_name = crop[0]
        print(f"\n--- {crop_name.upper()} ---")
        diseases = cursor.execute('SELECT disease_name, symptoms, prevention_steps FROM diseases WHERE crop = ?', (crop_name,)).fetchall()
        for d in diseases:
            print(f"Disease: {d[0]}")
            # print(f"Symptoms: {d[1][:50]}...")
            
    conn.close()
except Exception as e:
    print(f"Error: {e}")
