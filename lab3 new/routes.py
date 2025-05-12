from flask import request, jsonify, Flask
from flask_restful import Resource, Api
from models import db, UserRole, PrescriptionType
from functools import wraps
import jwt
from datetime import datetime, timedelta
import bcrypt

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this to a secure secret key in production

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.secret_key, algorithms=["HS256"])
            current_user = db.get_user(data['user_id'])
            if not current_user:
                return jsonify({'message': 'Invalid token!'}), 401
        except:
            return jsonify({'message': 'Invalid token!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):
            if UserRole(current_user['role']) not in roles:
                return jsonify({'message': 'Unauthorized!'}), 403
            return f(current_user, *args, **kwargs)
        return decorated
    return decorator

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not all(k in data for k in ('username', 'password', 'role', 'name')):
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        role = UserRole(data['role'])
    except ValueError:
        return jsonify({'message': 'Invalid role'}), 400

    # Check if username already exists
    if db.get_user_by_username(data['username']):
        return jsonify({'message': 'Username already exists'}), 400

    # Hash the password
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Additional fields based on role
    kwargs = {}
    if role == UserRole.DOCTOR:
        if 'specialization' not in data:
            return jsonify({'message': 'Specialization required for doctors'}), 400
        kwargs['specialization'] = data['specialization']
    elif role == UserRole.NURSE:
        if 'department' not in data:
            return jsonify({'message': 'Department required for nurses'}), 400
        kwargs['department'] = data['department']
    elif role == UserRole.PATIENT:
        kwargs['doctor_id'] = data.get('doctor_id')

    user = db.add_user(
        username=data['username'],
        password=hashed_password,
        role=role,
        name=data['name'],
        **kwargs
    )

    if not user:
        return jsonify({'message': 'Failed to create user'}), 400

    return jsonify({
        'message': 'User registered successfully',
        'user_id': user['id'],
        'role': user['role']
    }), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not all(k in data for k in ('username', 'password')):
        return jsonify({'message': 'Missing username or password'}), 400

    user = db.get_user_by_username(data['username'])
    if not user or not bcrypt.checkpw(data['password'].encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({'message': 'Invalid credentials'}), 401

    token = jwt.encode({
        'user_id': user['id'],
        'role': user['role'],
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, app.secret_key)

    return jsonify({
        'token': token,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'name': user['name']
        }
    })

@app.route('/profile', methods=['GET'])
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
        doctor = db.get_doctor_by_user_id(current_user['id'])
        if doctor:
            profile['specialization'] = doctor['specialization']
    elif UserRole(current_user['role']) == UserRole.NURSE:
        nurse = db.get_nurse_by_user_id(current_user['id'])
        if nurse:
            profile['department'] = nurse['department']
    elif UserRole(current_user['role']) == UserRole.PATIENT:
        patient = db.get_patient_by_user_id(current_user['id'])
        if patient:
            profile['admission_date'] = patient['admission_date']
            profile['discharge_date'] = patient['discharge_date']
            profile['current_diagnosis'] = patient['current_diagnosis']
            profile['final_diagnosis'] = patient['final_diagnosis']

    return jsonify(profile)

@app.route('/users', methods=['GET'])
@token_required
@role_required([UserRole.ADMIN])
def get_all_users(current_user):
    users = db.get_all_users()
    return jsonify(users)

@app.route('/patients/<int:patient_id>/diagnosis', methods=['PUT'])
@token_required
@role_required([UserRole.DOCTOR])
def update_patient_diagnosis(current_user, patient_id):
    data = request.get_json()
    if 'diagnosis' not in data:
        return jsonify({'message': 'Diagnosis is required'}), 400

    # Get the patient
    patient = db.get_patient_by_user_id(patient_id)
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404

    # Update the diagnosis
    conn = db.get_connection()
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

@app.route('/prescriptions', methods=['POST'])
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

    # Get doctor's ID
    doctor = db.get_doctor_by_user_id(current_user['id'])
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404

    # Create prescription
    prescription = db.add_prescription(
        patient_id=data['patient_id'],
        doctor_id=doctor['id'],
        prescription_type=prescription_type,
        description=data['description']
    )

    if not prescription:
        return jsonify({'message': 'Failed to create prescription'}), 400

    return jsonify(prescription), 201

@app.route('/prescriptions/<int:prescription_id>/complete', methods=['POST'])
@token_required
@role_required([UserRole.DOCTOR, UserRole.NURSE])
def complete_prescription(current_user, prescription_id):
    # Get the prescription
    prescription = db.get_prescription(prescription_id)
    if not prescription:
        return jsonify({'message': 'Prescription not found'}), 404

    # Check if the user can complete this type of prescription
    if UserRole(current_user['role']) == UserRole.NURSE:
        prescription_type = PrescriptionType(prescription['prescription_type'])
        if prescription_type == PrescriptionType.SURGERY:
            return jsonify({'message': 'Nurses cannot complete surgery prescriptions'}), 403

    # Complete the prescription
    updated_prescription = db.complete_prescription(prescription_id, current_user['id'])
    if not updated_prescription:
        return jsonify({'message': 'Failed to complete prescription'}), 400

    return jsonify(updated_prescription)

@app.route('/patients/<int:patient_id>/prescriptions', methods=['GET'])
@token_required
@role_required([UserRole.DOCTOR, UserRole.NURSE, UserRole.PATIENT])
def get_patient_prescriptions(current_user, patient_id):
    # Check if the user has permission to view these prescriptions
    if UserRole(current_user['role']) == UserRole.PATIENT and current_user['id'] != patient_id:
        return jsonify({'message': 'Unauthorized to view other patients\' prescriptions'}), 403

    prescriptions = db.get_patient_prescriptions(patient_id)
    return jsonify(prescriptions)

@app.route('/patients/<int:patient_id>/discharge', methods=['POST'])
@token_required
@role_required([UserRole.DOCTOR])
def discharge_patient(current_user, patient_id):
    data = request.get_json()
    if 'final_diagnosis' not in data:
        return jsonify({'message': 'Final diagnosis is required'}), 400

    # Get the patient
    patient = db.get_patient_by_id(patient_id)
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404

    # Check if patient is already discharged
    if patient['discharge_date']:
        return jsonify({'message': 'Patient is already discharged'}), 400

    # Discharge the patient
    updated_patient = db.discharge_patient(patient_id, data['final_diagnosis'])
    if not updated_patient:
        return jsonify({'message': 'Failed to discharge patient'}), 400

    return jsonify({
        'message': 'Patient discharged successfully',
        'patient': {
            'id': updated_patient['id'],
            'discharge_date': updated_patient['discharge_date'],
            'final_diagnosis': updated_patient['final_diagnosis']
        }
    })

if __name__ == '__main__':
    app.run(debug=True) 
