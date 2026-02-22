import sqlite3

conn = sqlite3.connect('database/crop_diagnosis.db')
cursor = conn.cursor()

print("=== TOMATO DISEASES ===")
rows = cursor.execute('SELECT disease_name, symptoms FROM diseases WHERE crop = "tomato"').fetchall()
for r in rows:
    print(f"  {r[0]}: {r[1][:50]}...")

print("\n=== POTATO DISEASES ===")
rows = cursor.execute('SELECT disease_name, symptoms FROM diseases WHERE crop = "potato"').fetchall()
for r in rows:
    print(f"  {r[0]}: {r[1][:50]}...")

conn.close()
