from flask import Blueprint, jsonify
from models.enums.user_enums import UserRole
from models.database.hospital_db import db
from ..common.decorators import token_required, role_required

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    profile = {
        'id': current_user['id'],
        'username': current_user['username'],
        'role': current_user['role'],
        'name': current_user['name']
    }

    # Add role-specific information
    if UserRole(current_user['role']) == UserRole.DOCTOR:
        doctor = db.users.get_doctor_by_user_id(current_user['id'])
        if doctor:
            profile['specialization'] = doctor['specialization']
    elif UserRole(current_user['role']) == UserRole.NURSE:
        nurse = db.users.get_nurse_by_user_id(current_user['id'])
        if nurse:
            profile['department'] = nurse['department']
    elif UserRole(current_user['role']) == UserRole.PATIENT:
        patient = db.patients.get_patient_by_user_id(current_user['id'])
        if patient:
            profile['admission_date'] = patient['admission_date']
            profile['discharge_date'] = patient['discharge_date']
            profile['current_diagnosis'] = patient['current_diagnosis']
            profile['final_diagnosis'] = patient['final_diagnosis']

    return jsonify(profile)

@profile_bp.route('/users', methods=['GET'])
@token_required
@role_required([UserRole.ADMIN])
def get_all_users(current_user):
    users = db.users.get_all_users()
    return jsonify(users) 