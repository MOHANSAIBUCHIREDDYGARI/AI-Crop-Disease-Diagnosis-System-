import json
import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_connection import db

def seed_database():
    """Populate database with initial data"""
    
    print("Starting database seeding...")
    
    
    seed_dir = os.path.dirname(os.path.abspath(__file__))
    
    
    print("\nSeeding diseases...")
    with open(os.path.join(seed_dir, 'diseases.json'), 'r', encoding='utf-8') as f:
        diseases = json.load(f)
    
    for disease in diseases:
        try:
            db.execute_insert(
                '''INSERT OR REPLACE INTO diseases 
                   (crop, disease_name, description, symptoms, prevention_steps, is_healthy)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (
                    disease['crop'],
                    disease['disease_name'],
                    disease['description'],
                    disease['symptoms'],
                    disease['prevention_steps'],
                    disease['is_healthy']
                )
            )
            print(f"  ✓ Added: {disease['crop']} - {disease['disease_name']}")
        except Exception as e:
            print(f"  ✗ Error adding {disease['disease_name']}: {e}")
    
    
    print("\nSeeding pesticides...")
    with open(os.path.join(seed_dir, 'pesticides.json'), 'r', encoding='utf-8') as f:
        pesticides = json.load(f)
    
    for pesticide in pesticides:
        try:
            db.execute_insert(
                '''INSERT OR REPLACE INTO pesticides 
                   (name, type, target_diseases, dosage_per_acre, frequency, 
                    cost_per_liter, is_organic, is_government_approved, warnings, incompatible_with)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    pesticide['name'],
                    pesticide['type'],
                    pesticide['target_diseases'],
                    pesticide['dosage_per_acre'],
                    pesticide['frequency'],
                    pesticide['cost_per_liter'],
                    pesticide['is_organic'],
                    pesticide['is_government_approved'],
                    pesticide['warnings'],
                    pesticide['incompatible_with']
                )
            )
            print(f"  ✓ Added: {pesticide['name']} ({pesticide['type']})")
        except Exception as e:
            print(f"  ✗ Error adding {pesticide['name']}: {e}")
    
    print("\n✅ Database seeding completed successfully!")
    
    
    disease_count = db.execute_query("SELECT COUNT(*) as count FROM diseases")[0]['count']
    pesticide_count = db.execute_query("SELECT COUNT(*) as count FROM pesticides")[0]['count']
    
    print(f"\nDatabase Statistics:")
    print(f"  - Diseases: {disease_count}")
    print(f"  - Pesticides: {pesticide_count}")

if __name__ == '__main__':
    seed_database()
