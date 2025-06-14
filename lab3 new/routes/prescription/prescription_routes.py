from flask import Blueprint, request, jsonify
from models.enums.user_enums import UserRole, PrescriptionType
from models.database.hospital_db import db
from ..common.decorators import token_required, role_required

prescription_bp = Blueprint('prescription', __name__)

@prescription_bp.route('/prescriptions', methods=['POST'])
@token_required
@role_required([UserRole.DOCTOR])
def create_prescription(current_user):
    data = request.get_json()
    if not all(k in data for k in ('patient_id', 'prescription_type', 'description')):
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        prescription_type = PrescriptionType(data['prescription_type'])
    except ValueError:
        return jsonify({'message': 'Invalid prescription type'}), 400

    # Check if patient exists
    patient = db.patients.get_patient_by_id(data['patient_id'])
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404

    # Get doctor's ID
    doctor = db.users.get_doctor_by_user_id(current_user['id'])
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404

    # Create prescription
    prescription = db.prescriptions.add_prescription(
        patient_id=data['patient_id'],
        doctor_id=doctor['id'],
        prescription_type=prescription_type,
        description=data['description']
    )

    if not prescription:
        return jsonify({'message': 'Prescription not created'}), 400

    return jsonify(prescription), 201

@prescription_bp.route('/prescriptions/<int:prescription_id>/complete', methods=['POST'])
@token_required
@role_required([UserRole.DOCTOR, UserRole.NURSE])
def complete_prescription(current_user, prescription_id):
    prescription = db.prescriptions.complete_prescription(prescription_id, current_user['id'])
    if not prescription:
        return jsonify({'message': 'Prescription not found'}), 404
    return jsonify(prescription)

@prescription_bp.route('/patients/<int:patient_id>/prescriptions', methods=['GET'])
@token_required
@role_required([UserRole.DOCTOR, UserRole.NURSE, UserRole.PATIENT])
def get_patient_prescriptions(current_user, patient_id):
    # Check if patient exists
    patient = db.patients.get_patient_by_id(patient_id)
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404
        
    prescriptions = db.prescriptions.get_patient_prescriptions(patient_id)
    return jsonify(prescriptions) 