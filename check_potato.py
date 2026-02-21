import sqlite3

conn = sqlite3.connect('database/crop_diagnosis.db')
cursor = conn.cursor()

print("=== POTATO DISEASES ===")
rows = cursor.execute('SELECT disease_name FROM diseases WHERE crop = "potato"').fetchall()
for r in rows:
    print(f"  '{r[0]}'")

print("\n=== Checking for 'Early Blight' ===")
# Try different variations
variations = [
    "Early Blight",
    "Early_Blight", 
    "Potato___Early_Blight",
    "Potato___Early blight",
    "early blight"
]

for var in variations:
    result = cursor.execute('SELECT disease_name FROM diseases WHERE crop = "potato" AND disease_name = ?', (var,)).fetchall()
    if result:
        print(f"  ✅ FOUND: '{var}'")
    else:
        print(f"  ❌ NOT FOUND: '{var}'")

conn.close()
