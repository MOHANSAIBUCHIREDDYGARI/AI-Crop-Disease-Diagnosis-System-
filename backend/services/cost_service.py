from typing import Dict, List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.pesticide_service import get_severity_based_recommendations

def calculate_treatment_cost(
    pesticides: List[Dict],
    land_area: float,
    severity_percent: float
) -> Dict:
    """
    Calculate treatment cost based on pesticides and land area
    
    Args:
        pesticides: List of recommended pesticides
        land_area: Land area in acres
        severity_percent: Disease severity percentage
        
    Returns:
        Dictionary with cost breakdown
    """
    if not pesticides:
        return {
            'pesticide_cost': 0,
            'labor_cost': 0,
            'total_treatment_cost': 0,
            'applications_needed': 0
        }
    
    
    if severity_percent < 5:
        applications = 1  
    elif severity_percent < 25:
        applications = 2  
    elif severity_percent < 50:
        applications = 3  
    else:
        applications = 4  
    
    
    total_pesticide_cost = 0
    pesticide_details = []
    
    for pesticide in pesticides[:3]:  
        
        dosage_text = pesticide.get('dosage_per_acre', '1 liter')
        quantity_per_acre = extract_quantity(dosage_text)
        
        
        total_quantity = quantity_per_acre * land_area * applications
        
        
        cost_per_unit = pesticide.get('cost_per_liter', 500)
        pesticide_cost = total_quantity * cost_per_unit
        
        total_pesticide_cost += pesticide_cost
        
        pesticide_details.append({
            'name': pesticide['name'],
            'quantity_per_application': quantity_per_acre * land_area,
            'total_quantity': total_quantity,
            'cost_per_unit': cost_per_unit,
            'total_cost': pesticide_cost
        })
    
    
    labor_cost_per_acre = 200  
    total_labor_cost = labor_cost_per_acre * land_area * applications
    
    
    total_treatment_cost = total_pesticide_cost + total_labor_cost
    
    return {
        'pesticide_cost': round(total_pesticide_cost, 2),
        'labor_cost': round(total_labor_cost, 2),
        'total_treatment_cost': round(total_treatment_cost, 2),
        'applications_needed': applications,
        'pesticide_details': pesticide_details,
        'land_area': land_area
    }

def calculate_prevention_cost(land_area: float, crop: str) -> Dict:
    """
    Calculate prevention cost for healthy crop maintenance
    
    Args:
        land_area: Land area in acres
        crop: Crop type
        
    Returns:
        Dictionary with prevention cost breakdown
    """
    
    preventive_spray_cost = 300  
    monitoring_cost = 100  
    good_practices_cost = 200  
    
    
    preventive_applications = 2
    
    total_prevention_cost = (
        (preventive_spray_cost * preventive_applications * land_area) +
        (monitoring_cost * land_area) +
        (good_practices_cost * land_area)
    )
    
    return {
        'preventive_spray_cost': preventive_spray_cost * preventive_applications * land_area,
        'monitoring_cost': monitoring_cost * land_area,
        'good_practices_cost': good_practices_cost * land_area,
        'total_prevention_cost': round(total_prevention_cost, 2),
        'applications': preventive_applications,
        'land_area': land_area
    }

def calculate_total_cost(
    disease_name: str,
    severity_percent: float,
    land_area: float,
    crop: str,
    include_prevention: bool = True
) -> Dict:
    """
    Calculate total cost including treatment and prevention
    
    Args:
        disease_name: Name of the disease
        severity_percent: Disease severity percentage
        land_area: Land area in acres
        crop: Crop type
        include_prevention: Whether to include prevention cost
        
    Returns:
        Complete cost breakdown
    """
    
    recommendations = get_severity_based_recommendations(disease_name, severity_percent, crop)
    pesticides = recommendations.get('recommended_pesticides', [])
    
    
    treatment = calculate_treatment_cost(pesticides, land_area, severity_percent)
    
    
    prevention = calculate_prevention_cost(land_area, crop) if include_prevention else {
        'total_prevention_cost': 0
    }
    
    
    total_cost = treatment['total_treatment_cost'] + prevention['total_prevention_cost']
    
    
    cost_comparison = {
        'treatment_cost': treatment['total_treatment_cost'],
        'prevention_cost': prevention['total_prevention_cost'],
        'total_cost': round(total_cost, 2),
        'savings_with_prevention': round(
            treatment['total_treatment_cost'] - prevention['total_prevention_cost'], 2
        ) if prevention['total_prevention_cost'] > 0 else 0
    }
    
    return {
        'treatment': treatment,
        'prevention': prevention,
        'comparison': cost_comparison,
        'severity_level': recommendations.get('severity_level', 'Unknown'),
        'urgency': recommendations.get('urgency', 'medium'),
        'land_area': land_area,
        'crop': crop,
        'disease': disease_name
    }

def extract_quantity(dosage_text: str) -> float:
    """
    Extract numeric quantity from dosage text
    
    Args:
        dosage_text: Dosage text like "2-3 kg" or "500 ml"
        
    Returns:
        Average quantity as float
    """
    import re
    
    
    numbers = re.findall(r'\d+\.?\d*', dosage_text)
    
    if not numbers:
        return 1.0  
    
    
    if len(numbers) >= 2:
        return (float(numbers[0]) + float(numbers[1])) / 2
    
    
    quantity = float(numbers[0])
    
    
    if 'ml' in dosage_text.lower() or 'gram' in dosage_text.lower():
        quantity = quantity / 1000
    
    return quantity

def generate_cost_report(cost_data: Dict) -> str:
    """
    Generate a formatted cost report
    
    Args:
        cost_data: Cost calculation data
        
    Returns:
        Formatted report string
    """
    report = f"""
╔══════════════════════════════════════════════════════════╗
║           CROP DISEASE TREATMENT COST REPORT             ║
╚══════════════════════════════════════════════════════════╝

Crop: {cost_data['crop'].title()}
Disease: {cost_data['disease']}
Severity: {cost_data['severity_level']} ({cost_data['treatment']['applications_needed']} applications needed)
Land Area: {cost_data['land_area']} acres

─────────────────────────────────────────────────────────────
TREATMENT COST BREAKDOWN
─────────────────────────────────────────────────────────────
Pesticides Cost:        ₹ {cost_data['treatment']['pesticide_cost']:,.2f}
Labor Cost:             ₹ {cost_data['treatment']['labor_cost']:,.2f}
Total Treatment Cost:   ₹ {cost_data['treatment']['total_treatment_cost']:,.2f}

─────────────────────────────────────────────────────────────
PREVENTION COST (Future)
─────────────────────────────────────────────────────────────
Preventive Measures:    ₹ {cost_data['prevention']['total_prevention_cost']:,.2f}

─────────────────────────────────────────────────────────────
TOTAL ESTIMATED COST
─────────────────────────────────────────────────────────────
Treatment + Prevention: ₹ {cost_data['comparison']['total_cost']:,.2f}

Note: Prevention is {((cost_data['prevention']['total_prevention_cost'] / cost_data['treatment']['total_treatment_cost']) * 100):.1f}% 
of treatment cost. Regular prevention can save money!

Urgency Level: {cost_data['urgency'].upper()}
"""
    return report

def get_cost_per_acre_comparison(disease_name: str, crop: str) -> Dict:
    """
    Get cost comparison per acre for different severity levels
    
    Args:
        disease_name: Name of the disease
        crop: Crop type
        
    Returns:
        Cost comparison for different severity levels
    """
    severity_levels = [
        ('Healthy', 2),
        ('Early', 15),
        ('Moderate', 40),
        ('Severe', 70)
    ]
    
    comparison = {}
    
    for level_name, severity in severity_levels:
        cost_data = calculate_total_cost(disease_name, severity, 1.0, crop)
        comparison[level_name] = {
            'treatment_cost_per_acre': cost_data['treatment']['total_treatment_cost'],
            'applications': cost_data['treatment']['applications_needed'],
            'severity_percent': severity
        }
    
    return comparison
