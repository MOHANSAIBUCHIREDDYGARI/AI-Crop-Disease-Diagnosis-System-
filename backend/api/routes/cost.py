from flask import Blueprint, request, jsonify
import sys
import os
from bson.objectid import ObjectId

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
        
        # Verify authentication token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        token_data = verify_token(token)
        
        if not token_data['valid']:
            return jsonify({'error': token_data['error']}), 401
        
        user_id = token_data['user_id']
        data = request.get_json()
        
        # Get parameters from request
        diagnosis_id = data.get('diagnosis_id')
        land_area = data.get('land_area', type=float)
        
        # Validate parameters
        if not diagnosis_id or not land_area:
            return jsonify({'error': 'diagnosis_id and land_area required'}), 400
        
        if land_area <= 0 or land_area > 10000:
            return jsonify({'error': 'Invalid land area'}), 400
        
        # Fetch diagnosis details
        diagnosis_collection = db.get_collection('diagnosis_history')
        try:
             oid_diag = ObjectId(diagnosis_id)
        except:
             return jsonify({'error': 'Invalid diagnosis ID'}), 400

        diagnosis = diagnosis_collection.find_one({'_id': oid_diag, 'user_id': user_id})
        
        if not diagnosis:
            return jsonify({'error': 'Diagnosis not found'}), 404
        
        
        # Calculate costs based on disease and land area
        cost_data = calculate_total_cost(
            diagnosis['disease'],
            diagnosis['severity_percent'],
            land_area,
            diagnosis['crop']
        )
        
        # Save calculation to database
        cost_collection = db.get_collection('cost_calculations')
        
        cost_doc = {
            'diagnosis_id': str(diagnosis['_id']),
            'land_area': land_area,
            'treatment_cost': cost_data['comparison']['treatment_cost'],
            'prevention_cost': cost_data['comparison']['prevention_cost'],
            'total_cost': cost_data['comparison']['total_cost']
        }
        
        result = cost_collection.insert_one(cost_doc)
        cost_id = str(result.inserted_id)
        
        # Get user's preferred language
        users_collection = db.get_collection('users')
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        language = user.get('preferred_language', 'en') if user else 'en'
        
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

@cost_bp.route('/report/<diagnosis_id>', methods=['GET'])
def get_cost_report(diagnosis_id):
    """Get downloadable cost report"""
    try:
        
        # Verify authentication token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        token_data = verify_token(token)
        
        if not token_data['valid']:
            return jsonify({'error': token_data['error']}), 401
        
        user_id = token_data['user_id']
        
        # In MongoDB, we typically do two queries instead of a JOIN, 
        # or use $lookup aggregation if needed. Simple parsing is easier here.
        
        cost_collection = db.get_collection('cost_calculations')
        cost_calc = cost_collection.find_one({'diagnosis_id': diagnosis_id})
        
        if not cost_calc:
             return jsonify({'error': 'Cost report not found'}), 404
             
        # Now get the diagnosis details to verify ownership and get crop info
        diagnosis_collection = db.get_collection('diagnosis_history')
        try:
             oid_diag = ObjectId(diagnosis_id)
        except:
             return jsonify({'error': 'Invalid diagnosis ID'}), 400
             
        diagnosis = diagnosis_collection.find_one({'_id': oid_diag, 'user_id': user_id})
        
        if not diagnosis:
            # If we liked the cost but couldn't find the diagnosis for THIS user, it's unauthorized
            return jsonify({'error': 'Diagnosis not found or unauthorized'}), 404
        
        
        # Structure the data for the report
        cost_data = {
            'crop': diagnosis['crop'],
            'disease': diagnosis['disease'],
            'severity_level': diagnosis['stage'],
            'treatment': {
                'pesticide_cost': cost_calc['treatment_cost'] * 0.7,  # Estimated 70% for pesticides
                'labor_cost': cost_calc['treatment_cost'] * 0.3,      # Estimated 30% for labor
                'total_treatment_cost': cost_calc['treatment_cost'],
                'applications_needed': 2 if diagnosis['severity_percent'] < 25 else 3
            },
            'prevention': {
                'total_prevention_cost': cost_calc['prevention_cost']
            },
            'comparison': {
                'total_cost': cost_calc['total_cost']
            },
            'land_area': cost_calc['land_area'],
            'urgency': 'high' if diagnosis['severity_percent'] > 50 else 'medium'
        }
        
        # Generate the formatted report
        report = generate_cost_report(cost_data)
        
        return jsonify({'report': report, 'cost_data': cost_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
