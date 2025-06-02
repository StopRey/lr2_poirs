from flask import Blueprint, request, jsonify
from models.enums.user_enums import UserRole
from models.database.hospital_db import db
from ..common.decorators import token_required, role_required

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/patients/<int:patient_id>/diagnosis', methods=['PUT'])
@token_required
@role_required([UserRole.DOCTOR])
def update_patient_diagnosis(current_user, patient_id):
    data = request.get_json()
    if 'diagnosis' not in data:
        return jsonify({'message': 'Diagnosis is required'}), 400

    # Get the patient
    patient = db.patients.get_patient_by_user_id(patient_id)
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404

    # Update the diagnosis
    conn = db.db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'UPDATE patients SET current_diagnosis = ? WHERE user_id = ?',
            (data['diagnosis'], patient_id)
        )
        conn.commit()
        return jsonify({'message': 'Diagnosis updated successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'message': 'Failed to update diagnosis'}), 400
    finally:
        conn.close()

@patient_bp.route('/patients/<int:patient_id>/discharge', methods=['POST'])
@token_required
@role_required([UserRole.DOCTOR])
def discharge_patient(current_user, patient_id):
    data = request.get_json()
    if 'final_diagnosis' not in data:
        return jsonify({'message': 'Final diagnosis is required'}), 400

    patient = db.patients.discharge_patient(patient_id, data['final_diagnosis'])
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404
    return jsonify(patient)

@patient_bp.route('/patients/search', methods=['GET'])
@token_required
@role_required([UserRole.DOCTOR, UserRole.NURSE])
def search_patients(current_user):
    # Get filter parameters from query string
    name = request.args.get('name', '')
    diagnosis = request.args.get('diagnosis', '')
    status = request.args.get('status', '')  # active/discharged
    admission_date = request.args.get('admission_date', '')
    
    # Get filtered patients from database
    patients = db.patients.search_patients(
        name=name,
        diagnosis=diagnosis,
        status=status,
        admission_date=admission_date
    )
    
    return jsonify(patients) 