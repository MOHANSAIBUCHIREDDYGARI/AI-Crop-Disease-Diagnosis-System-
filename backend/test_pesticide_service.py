import sys
import os
from pprint import pprint

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.pesticide_service import get_pesticides_for_disease, get_pesticide_by_name

def test_pesticide_service():
    print("--- Testing Pesticide Service with MongoDB ---")
    
    # Test 1: Get pesticides for a disease
    disease = "Bacterial Spot"
    crop = "Tomato"
    print(f"\n1. Searching for pesticides for: {crop} - {disease}")
    results = get_pesticides_for_disease(disease, crop)
    
    if results:
        print(f"PASS: Found {len(results)} pesticides.")
        for p in results[:3]:
            print(f" - {p['name']} (Organic: {p['is_organic']}, Cost: {p['cost_per_liter']})")
    else:
        print("WARN: No pesticides found. Checking if database has ANY pesticides...")
        # Check if DB is empty
        from database.db_connection import db
        count = db.get_collection('pesticides').count_documents({})
        print(f"Total pesticides in DB: {count}")
        
    # Test 2: Get specific pesticide
    if results:
        name = results[0]['name']
        print(f"\n2. Fetching details for: {name}")
        details = get_pesticide_by_name(name)
        if details:
            print("PASS: Successfully fetched details.")
            pprint(details)
        else:
            print("FAIL: Could not fetch details.")
            
if __name__ == "__main__":
    test_pesticide_service()
