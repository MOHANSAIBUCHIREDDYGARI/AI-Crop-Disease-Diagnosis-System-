from flask import Blueprint, request, jsonify
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.db_connection import db
from services.cost_service import calculate_total_cost, generate_cost_report
from services.language_service import translate_text
from api.routes.user import verify_token

cost_bp = Blueprint('cost', __name__)

@cost_bp.route('/calculate', methods=['POST'])
def calculate_cost():
    """Calculate treatment and prevention costs"""
    try:
        # Verify token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        token_data = verify_token(token)
        
        if not token_data['valid']:
            return jsonify({'error': token_data['error']}), 401
        
        user_id = token_data['user_id']
        data = request.get_json()
        
        # Validate input
        diagnosis_id = data.get('diagnosis_id')
        land_area = data.get('land_area', type=float)
        
        if not diagnosis_id or not land_area:
            return jsonify({'error': 'diagnosis_id and land_area required'}), 400
        
        if land_area <= 0 or land_area > 10000:
            return jsonify({'error': 'Invalid land area'}), 400
        
        # Get diagnosis details
        diagnosis = db.execute_query(
            'SELECT * FROM diagnosis_history WHERE id = ? AND user_id = ?',
            (diagnosis_id, user_id)
        )
        
        if not diagnosis:
            return jsonify({'error': 'Diagnosis not found'}), 404
        
        diagnosis = diagnosis[0]
        
        # Calculate costs
        cost_data = calculate_total_cost(
            diagnosis['disease'],
            diagnosis['severity_percent'],
            land_area,
            diagnosis['crop']
        )
        
        # Save cost calculation
        cost_id = db.execute_insert(
            '''INSERT INTO cost_calculations 
               (diagnosis_id, land_area, treatment_cost, prevention_cost, total_cost)
               VALUES (?, ?, ?, ?, ?)''',
            (
                diagnosis_id,
                land_area,
                cost_data['comparison']['treatment_cost'],
                cost_data['comparison']['prevention_cost'],
                cost_data['comparison']['total_cost']
            )
        )
        
        # Get user's language
        user = db.execute_query('SELECT preferred_language FROM users WHERE id = ?', (user_id,))
        language = user[0]['preferred_language'] if user else 'en'
        
        # Translate treatment approach if needed
        if language != 'en':
            cost_data['treatment']['treatment_approach'] = translate_text(
                cost_data['treatment'].get('treatment_approach', ''),
                language
            )
        
        response = {
            'cost_id': cost_id,
            'cost_data': cost_data,
            'language': language
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cost_bp.route('/report/<int:diagnosis_id>', methods=['GET'])
def get_cost_report(diagnosis_id):
    """Get downloadable cost report"""
    try:
        # Verify token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        token_data = verify_token(token)
        
        if not token_data['valid']:
            return jsonify({'error': token_data['error']}), 401
        
        user_id = token_data['user_id']
        
        # Get cost calculation
        cost_calc = db.execute_query(
            '''SELECT cc.*, dh.crop, dh.disease, dh.severity_percent, dh.stage
               FROM cost_calculations cc
               JOIN diagnosis_history dh ON cc.diagnosis_id = dh.id
               WHERE cc.diagnosis_id = ? AND dh.user_id = ?''',
            (diagnosis_id, user_id)
        )
        
        if not cost_calc:
            return jsonify({'error': 'Cost report not found'}), 404
        
        cost_calc = cost_calc[0]
        
        # Reconstruct cost data for report
        cost_data = {
            'crop': cost_calc['crop'],
            'disease': cost_calc['disease'],
            'severity_level': cost_calc['stage'],
            'treatment': {
                'pesticide_cost': cost_calc['treatment_cost'] * 0.7,  # Approximate
                'labor_cost': cost_calc['treatment_cost'] * 0.3,
                'total_treatment_cost': cost_calc['treatment_cost'],
                'applications_needed': 2 if cost_calc['severity_percent'] < 25 else 3
            },
            'prevention': {
                'total_prevention_cost': cost_calc['prevention_cost']
            },
            'comparison': {
                'total_cost': cost_calc['total_cost']
            },
            'land_area': cost_calc['land_area'],
            'urgency': 'high' if cost_calc['severity_percent'] > 50 else 'medium'
        }
        
        # Generate report
        report = generate_cost_report(cost_data)
        
        return jsonify({'report': report, 'cost_data': cost_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
