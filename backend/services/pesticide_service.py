import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.db_connection import db
from typing import List, Dict

def get_pesticides_for_disease(disease_name: str, crop: str, prefer_organic: bool = False) -> List[Dict]:
    """
    Get recommended pesticides for a specific disease
    
    Args:
        disease_name: Name of the disease
        crop: Crop type
        prefer_organic: Whether to prefer organic pesticides
        
    Returns:
        List of pesticide recommendations
    """
    # Clean disease name for matching
    disease_clean = disease_name.replace('___', ' ').replace('_', ' ')
    
    # Query pesticides that target this disease
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
    
    # If prefer organic, sort organic first
    if prefer_organic:
        pesticides.sort(key=lambda x: (not x['is_organic'], x['cost_per_liter']))
    
    return pesticides

def get_pesticide_by_name(name: str) -> Dict:
    """Get pesticide information by name"""
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
    Check if pesticides are compatible with each other
    
    Args:
        pesticide_names: List of pesticide names
        
    Returns:
        Dictionary with compatibility information
    """
    incompatibilities = []
    
    for i, name1 in enumerate(pesticide_names):
        pesticide1 = get_pesticide_by_name(name1)
        if not pesticide1:
            continue
        
        incompatible_with = pesticide1.get('incompatible_with', '')
        if not incompatible_with:
            continue
        
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
    Get pesticide recommendations based on disease severity
    
    Args:
        disease_name: Name of the disease
        severity_percent: Disease severity percentage
        crop: Crop type
        
    Returns:
        Dictionary with recommendations and treatment approach
    """
    # Get all pesticides for this disease
    all_pesticides = get_pesticides_for_disease(disease_name, crop)
    
    if not all_pesticides:
        return {
            'severity_level': get_severity_level(severity_percent),
            'recommended_pesticides': [],
            'treatment_approach': 'No specific pesticides found. Consult agricultural expert.',
            'urgency': 'medium'
        }
    
    severity_level = get_severity_level(severity_percent)
    
    # Determine treatment approach based on severity
    if severity_percent < 5:
        # Healthy or very early stage
        approach = 'Preventive measures recommended. Monitor regularly.'
        urgency = 'low'
        recommended = [p for p in all_pesticides if p['is_organic']][:2]
    elif severity_percent < 25:
        # Early stage - prefer organic
        approach = 'Early stage detected. Start with organic treatment.'
        urgency = 'medium'
        recommended = [p for p in all_pesticides if p['is_organic']][:3]
        if len(recommended) < 2:
            recommended.extend([p for p in all_pesticides if not p['is_organic']][:2])
    elif severity_percent < 50:
        # Moderate stage - combination approach
        approach = 'Moderate infection. Use effective fungicides/insecticides.'
        urgency = 'high'
        # Mix of organic and chemical
        recommended = all_pesticides[:4]
    else:
        # Severe stage - aggressive treatment
        approach = 'Severe infection. Immediate aggressive treatment required.'
        urgency = 'critical'
        # Prioritize most effective (usually chemical)
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
    """Get severity level name from percentage"""
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
    """Get application notes based on severity"""
    if severity_percent < 5:
        return 'Focus on prevention. Maintain good agricultural practices.'
    elif severity_percent < 25:
        return 'Apply pesticides at recommended intervals. Monitor progress closely.'
    elif severity_percent < 50:
        return 'Apply pesticides every 7-10 days. Remove severely infected parts.'
    else:
        return 'Immediate action required. Apply pesticides every 5-7 days. Consider removing heavily infected plants to prevent spread.'

def get_organic_alternatives(disease_name: str, crop: str) -> List[Dict]:
    """Get only organic pesticide alternatives"""
    all_pesticides = get_pesticides_for_disease(disease_name, crop, prefer_organic=True)
    return [p for p in all_pesticides if p['is_organic']]

def get_government_approved_pesticides(disease_name: str, crop: str) -> List[Dict]:
    """Get only government-approved pesticides"""
    all_pesticides = get_pesticides_for_disease(disease_name, crop)
    return [p for p in all_pesticides if p['is_government_approved']]
