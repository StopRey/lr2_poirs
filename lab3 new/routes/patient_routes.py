from flask import request, jsonify
from models.enums import UserRole
from models.database.hospital_db import db
from . import app
from .decorators import token_required, role_required

@app.route('/patients/<int:patient_id>/diagnosis', methods=['PUT'])
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
        return jsonify({'message': 'Failed to update diagnosis'}), 500
    finally:
        conn.close()

@app.route('/patients/<int:patient_id>/discharge', methods=['POST'])
@token_required
@role_required([UserRole.DOCTOR])
def discharge_patient(current_user, patient_id):
    data = request.get_json()
    if 'final_diagnosis' not in data:
        return jsonify({'message': 'Final diagnosis is required'}), 400

    patient = db.patients.discharge_patient(patient_id, data['final_diagnosis'])
    if not patient:
        return jsonify({'message': 'Failed to discharge patient'}), 400
    return jsonify(patient) 