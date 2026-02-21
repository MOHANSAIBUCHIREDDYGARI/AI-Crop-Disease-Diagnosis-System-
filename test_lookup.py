import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.db_connection import db

# Test the exact query that the API uses
crop = "potato"
disease = "Early Blight"

print(f"Testing query for: crop='{crop}', disease='{disease}'")

# Try exact match
disease_info = db.execute_query(
    'SELECT * FROM diseases WHERE crop = ? AND disease_name = ?',
    (crop, disease)
)

if disease_info:
    print(f"\n✅ FOUND! Disease info:")
    print(f"  Description: {disease_info[0]['description']}")
    print(f"  Symptoms: {disease_info[0]['symptoms']}")
    print(f"  Prevention: {disease_info[0]['prevention_steps']}")
else:
    print("\n❌ NOT FOUND")
