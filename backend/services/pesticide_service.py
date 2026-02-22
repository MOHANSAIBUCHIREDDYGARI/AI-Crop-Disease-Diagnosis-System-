import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.db_connection import db
from typing import List, Dict

def get_pesticides_for_disease(disease_name: str, crop: str, prefer_organic: bool = False) -> List[Dict]:
    """
    Search for medicines (pesticides) that cure the specific disease found.
    
    Args:
        disease_name: The name of the disease (e.g., Early Blight)
        prefer_organic: If True, we show rock-salt, neem oil, etc. first!
    """
    
    disease_clean = disease_name.replace('___', ' ').replace('_', ' ')
    
    # We look in our database for any pesticide that mentions this disease in its 'target_diseases'
    query = '''
        SELECT * FROM pesticides 
        WHERE target_diseases LIKE ? 
        ORDER BY is_organic DESC, cost_per_liter ASC
    '''
    
    results = db.execute_query(query, (f'%{disease_clean}%',))
    
    pesticides = []
    for row in results:
        pesticide = {
            'id': row['id'],
            'name': row['name'],
            'type': row['type'],
            'dosage_per_acre': row['dosage_per_acre'],
            'frequency': row['frequency'],
            'cost_per_liter': row['cost_per_liter'],
            'is_organic': bool(row['is_organic']),
            'is_government_approved': bool(row['is_government_approved']),
            'warnings': row['warnings'],
            'incompatible_with': row['incompatible_with']
        }
        pesticides.append(pesticide)
    
    # If the user loves organic, we make sure those are at the very top
    if prefer_organic:
        pesticides.sort(key=lambda x: (not x['is_organic'], x['cost_per_liter']))
    
    return pesticides

def get_pesticide_by_name(name: str) -> Dict:
    """Find details of a specific pesticide by its name."""
    query = 'SELECT * FROM pesticides WHERE name = ?'
    results = db.execute_query(query, (name,))
    
    if results:
        row = results[0]
        return {
            'id': row['id'],
            'name': row['name'],
            'type': row['type'],
            'target_diseases': row['target_diseases'],
            'dosage_per_acre': row['dosage_per_acre'],
            'frequency': row['frequency'],
            'cost_per_liter': row['cost_per_liter'],
            'is_organic': bool(row['is_organic']),
            'is_government_approved': bool(row['is_government_approved']),
            'warnings': row['warnings'],
            'incompatible_with': row['incompatible_with']
        }
    return None

def check_pesticide_compatibility(pesticide_names: List[str]) -> Dict:
    """
    Safety check! Can these two medicines be mixed?
    Mixing the wrong ones can be dangerous (like bleach and ammonia).
    """
    incompatibilities = []
    
    for i, name1 in enumerate(pesticide_names):
        pesticide1 = get_pesticide_by_name(name1)
        if not pesticide1:
            continue
        
        incompatible_with = pesticide1.get('incompatible_with', '')
        if not incompatible_with:
            continue
        
        # Check against every other pesticide in the list
        for name2 in pesticide_names[i+1:]:
            if name2.lower() in incompatible_with.lower():
                incompatibilities.append({
                    'pesticide1': name1,
                    'pesticide2': name2,
                    'warning': f'{name1} is incompatible with {name2}'
                })
    
    return {
        'is_compatible': len(incompatibilities) == 0,
        'incompatibilities': incompatibilities
    }

def get_severity_based_recommendations(disease_name: str, severity_percent: float, crop: str) -> Dict:
    """
    Smart Doctor Logic: 
    - If disease is mild (0-5%), just watch it.
    - If moderate (25-50%), use organic solutions.
    - If severe (>50%), use strong chemicals immediately.
    """
    
    all_pesticides = get_pesticides_for_disease(disease_name, crop)
    
    if not all_pesticides:
        return {
            'severity_level': get_severity_level(severity_percent),
            'recommended_pesticides': [],
            'treatment_approach': 'No specific pesticides found. Consult agricultural expert.',
            'urgency': 'medium'
        }
    
    severity_level = get_severity_level(severity_percent)
    
    # Logic for customized treatment plans
    if severity_percent < 5:
        # Just started - try not to use chemicals yet
        approach = 'Preventive measures recommended. Monitor regularly.'
        urgency = 'low'
        recommended = [p for p in all_pesticides if p['is_organic']][:2]
    elif severity_percent < 25:
        # Early stage - organic is usually enough
        approach = 'Early stage detected. Start with organic treatment.'
        urgency = 'medium'
        recommended = [p for p in all_pesticides if p['is_organic']][:3]
        # If no organic options, use mild chemicals
        if len(recommended) < 2:
            recommended.extend([p for p in all_pesticides if not p['is_organic']][:2])
    elif severity_percent < 50:
        # Getting serious - time for real medicine
        approach = 'Moderate infection. Use effective fungicides/insecticides.'
        urgency = 'high'
        # Mix of best options
        recommended = all_pesticides[:4]
    else:
        # Emergency! Save the crop!
        approach = 'Severe infection. Immediate aggressive treatment required.'
        urgency = 'critical'
        # Strong chemicals first
        recommended = [p for p in all_pesticides if not p['is_organic']][:3]
        if len(recommended) < 2:
            recommended.extend(all_pesticides[:3])
    
    return {
        'severity_level': severity_level,
        'severity_percent': severity_percent,
        'recommended_pesticides': recommended,
        'treatment_approach': approach,
        'urgency': urgency,
        'application_note': get_application_note(severity_percent)
    }

def get_severity_level(severity_percent: float) -> str:
    """Convert number (45%) to name (Moderate)"""
    if severity_percent < 5:
        return 'Healthy'
    elif severity_percent < 25:
        return 'Early Stage'
    elif severity_percent < 50:
        return 'Moderate'
    elif severity_percent < 75:
        return 'Severe'
    else:
        return 'Critical'

def get_application_note(severity_percent: float) -> str:
    """Give instructions on how often to spray based on how bad it is."""
    if severity_percent < 5:
        return 'Focus on prevention. Maintain good agricultural practices.'
    elif severity_percent < 25:
        return 'Apply pesticides at recommended intervals. Monitor progress closely.'
    elif severity_percent < 50:
        return 'Apply pesticides every 7-10 days. Remove severely infected parts.'
    else:
        return 'Immediate action required. Apply pesticides every 5-7 days. Consider removing heavily infected plants to prevent spread.'

def get_organic_alternatives(disease_name: str, crop: str) -> List[Dict]:
    """Get only the eco-friendly options."""
    all_pesticides = get_pesticides_for_disease(disease_name, crop, prefer_organic=True)
    return [p for p in all_pesticides if p['is_organic']]

def get_government_approved_pesticides(disease_name: str, crop: str) -> List[Dict]:
    """Get only the certified, safe-to-use pesticides."""
    all_pesticides = get_pesticides_for_disease(disease_name, crop)
    return [p for p in all_pesticides if p['is_government_approved']]
