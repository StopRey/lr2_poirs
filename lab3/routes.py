from flask import request, jsonify, Flask, session
from flask_restful import Resource, Api
from database import db
from datetime import datetime
from models import UserRole
from functools import wraps
import jwt

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
            if current_user.role not in roles:
                return jsonify({'message': 'Unauthorized!'}), 403
            return f(current_user, *args, **kwargs)
        return decorated
    return decorator

class PatientResource(Resource):
    def get(self, patient_id=None):
        if patient_id:
            patient = db.get_patient(patient_id)
            if not patient:
                return {'error': 'Patient not found'}, 404
            return {
                'id': patient.id,
                'name': patient.name,
                'admission_date': patient.admission_date.isoformat(),
                'discharge_date': patient.discharge_date.isoformat() if patient.discharge_date else None,
                'final_diagnosis': patient.final_diagnosis,
                'current_diagnosis': patient.current_diagnosis
            }
        return [{
            'id': p.id,
            'name': p.name,
            'admission_date': p.admission_date.isoformat(),
            'discharge_date': p.discharge_date.isoformat() if p.discharge_date else None
        } for p in db.patients.values()]

    def post(self):
        data = request.get_json()
        if not data or 'name' not in data:
            return {'error': 'Name is required'}, 400
        patient = db.add_patient(data['name'])
        return {
            'id': patient.id,
            'name': patient.name,
            'admission_date': patient.admission_date.isoformat()
        }, 201

    def put(self, patient_id):
        patient = db.get_patient(patient_id)
        if not patient:
            return {'error': 'Patient not found'}, 404
        
        data = request.get_json()
        if 'current_diagnosis' in data:
            patient.current_diagnosis = data['current_diagnosis']
        if 'final_diagnosis' in data and 'discharge' in data:
            patient = db.discharge_patient(patient_id, data['final_diagnosis'])
        
        db.update_patient(patient)
        return {
            'id': patient.id,
            'name': patient.name,
            'current_diagnosis': patient.current_diagnosis,
            'final_diagnosis': patient.final_diagnosis,
            'discharge_date': patient.discharge_date.isoformat() if patient.discharge_date else None
        }

class DoctorResource(Resource):
    def get(self, doctor_id=None):
        if doctor_id:
            doctor = db.get_doctor(doctor_id)
            if not doctor:
                return {'error': 'Doctor not found'}, 404
            return {
                'id': doctor.id,
                'name': doctor.name,
                'specialization': doctor.specialization
            }
        return [{
            'id': d.id,
            'name': d.name,
            'specialization': d.specialization
        } for d in db.doctors.values()]

    def post(self):
        data = request.get_json()
        if not data or 'name' not in data or 'specialization' not in data:
            return {'error': 'Name and specialization are required'}, 400
        doctor = db.add_doctor(data['name'], data['specialization'])
        return {
            'id': doctor.id,
            'name': doctor.name,
            'specialization': doctor.specialization
        }, 201

class NurseResource(Resource):
    def get(self, nurse_id=None):
        if nurse_id:
            nurse = db.get_nurse(nurse_id)
            if not nurse:
                return {'error': 'Nurse not found'}, 404
            return {
                'id': nurse.id,
                'name': nurse.name
            }
        return [{
            'id': n.id,
            'name': n.name
        } for n in db.nurses.values()]

    def post(self):
        data = request.get_json()
        if not data or 'name' not in data:
            return {'error': 'Name is required'}, 400
        nurse = db.add_nurse(data['name'])
        return {
            'id': nurse.id,
            'name': nurse.name
        }, 201

class PrescriptionResource(Resource):
    def get(self, prescription_id=None):
        if prescription_id:
            prescription = db.prescriptions.get(prescription_id)
            if not prescription:
                return {'error': 'Prescription not found'}, 404
            return {
                'id': prescription.id,
                'patient_id': prescription.patient_id,
                'doctor_id': prescription.doctor_id,
                'type': prescription.type,
                'description': prescription.description,
                'status': prescription.status,
                'assigned_to': prescription.assigned_to,
                'completed_by': prescription.completed_by,
                'completion_date': prescription.completion_date.isoformat() if prescription.completion_date else None
            }
        return [{
            'id': p.id,
            'patient_id': p.patient_id,
            'doctor_id': p.doctor_id,
            'type': p.type,
            'description': p.description,
            'status': p.status
        } for p in db.prescriptions.values()]

    def post(self):
        data = request.get_json()
        required_fields = ['patient_id', 'doctor_id', 'type', 'description', 'assigned_to']
        if not all(field in data for field in required_fields):
            return {'error': 'Missing required fields'}, 400
        
        prescription = db.add_prescription(
            data['patient_id'],
            data['doctor_id'],
            data['type'],
            data['description'],
            data['assigned_to']
        )
        if not prescription:
            return {'error': 'Invalid patient or doctor ID'}, 400
        
        return {
            'id': prescription.id,
            'patient_id': prescription.patient_id,
            'doctor_id': prescription.doctor_id,
            'type': prescription.type,
            'description': prescription.description,
            'status': prescription.status,
            'assigned_to': prescription.assigned_to
        }, 201

    def put(self, prescription_id):
        data = request.get_json()
        if 'completed_by' not in data:
            return {'error': 'completed_by is required'}, 400
        
        prescription = db.complete_prescription(prescription_id, data['completed_by'])
        if not prescription:
            return {'error': 'Prescription not found or already completed'}, 404
        
        return {
            'id': prescription.id,
            'status': prescription.status,
            'completed_by': prescription.completed_by,
            'completion_date': prescription.completion_date.isoformat()
        }

def init_routes(app):
    api = Api(app)
    api.add_resource(PatientResource, '/patients', '/patients/<int:patient_id>')
    api.add_resource(DoctorResource, '/doctors', '/doctors/<int:doctor_id>')
    api.add_resource(NurseResource, '/nurses', '/nurses/<int:nurse_id>')
    api.add_resource(PrescriptionResource, '/prescriptions', '/prescriptions/<int:prescription_id>')

    @app.route('/register', methods=['POST'])
    def register():
        data = request.get_json()
        if not all(k in data for k in ('username', 'password', 'role', 'name')):
            return jsonify({'message': 'Missing required fields'}), 400

        try:
            role = UserRole(data['role'])
        except ValueError:
            return jsonify({'message': 'Invalid role'}), 400

        user = db.add_user(
            username=data['username'],
            password=data['password'],
            role=role,
            name=data['name']
        )

        # Create corresponding doctor or nurse record
        if role == UserRole.DOCTOR:
            db.add_doctor(name=data['name'], specialization=data.get('specialization', ''), user_id=user.id)
        elif role == UserRole.NURSE:
            db.add_nurse(name=data['name'], user_id=user.id)

        return jsonify({'message': 'User registered successfully'}), 201

    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        if not all(k in data for k in ('username', 'password')):
            return jsonify({'message': 'Missing username or password'}), 400

        user = db.authenticate_user(data['username'], data['password'])
        if not user:
            return jsonify({'message': 'Invalid credentials'}), 401

        token = jwt.encode({
            'user_id': user.id,
            'role': user.role.value,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.secret_key)

        return jsonify({'token': token})

    @app.route('/patients', methods=['POST'])
    @token_required
    @role_required([UserRole.DOCTOR, UserRole.ADMIN])
    def add_patient(current_user):
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'message': 'Missing required fields'}), 400

        doctor = db.get_doctor_by_user_id(current_user.id)
        patient = db.add_patient(
            name=data['name'],
            assigned_doctor_id=doctor.id if doctor else None
        )
        return jsonify({
            'id': patient.id,
            'name': patient.name,
            'admission_date': patient.admission_date.isoformat()
        }), 201

    @app.route('/patients/<int:patient_id>/diagnosis', methods=['PUT'])
    @token_required
    @role_required([UserRole.DOCTOR])
    def update_diagnosis(current_user, patient_id):
        data = request.get_json()
        if not data or 'diagnosis' not in data:
            return jsonify({'message': 'Missing diagnosis'}), 400

        patient = db.get_patient(patient_id)
        if not patient:
            return jsonify({'message': 'Patient not found'}), 404

        doctor = db.get_doctor_by_user_id(current_user.id)
        if not doctor or patient.assigned_doctor_id != doctor.id:
            return jsonify({'message': 'Unauthorized to update this patient'}), 403

        patient.current_diagnosis = data['diagnosis']
        db.update_patient(patient)
        return jsonify({'message': 'Diagnosis updated successfully'})

    @app.route('/patients/<int:patient_id>/discharge', methods=['POST'])
    @token_required
    @role_required([UserRole.DOCTOR])
    def discharge_patient(current_user, patient_id):
        data = request.get_json()
        if not data or 'final_diagnosis' not in data:
            return jsonify({'message': 'Missing final diagnosis'}), 400

        doctor = db.get_doctor_by_user_id(current_user.id)
        if not doctor:
            return jsonify({'message': 'Doctor not found'}), 404

        patient = db.discharge_patient(patient_id, data['final_diagnosis'], doctor.id)
        if not patient:
            return jsonify({'message': 'Patient not found'}), 404

        return jsonify({'message': 'Patient discharged successfully'})

    @app.route('/prescriptions', methods=['POST'])
    @token_required
    @role_required([UserRole.DOCTOR])
    def add_prescription(current_user):
        data = request.get_json()
        if not all(k in data for k in ('patient_id', 'type', 'description', 'assigned_to')):
            return jsonify({'message': 'Missing required fields'}), 400

        doctor = db.get_doctor_by_user_id(current_user.id)
        if not doctor:
            return jsonify({'message': 'Doctor not found'}), 404

        prescription = db.add_prescription(
            patient_id=data['patient_id'],
            doctor_id=doctor.id,
            type=data['type'],
            description=data['description'],
            assigned_to=data['assigned_to']
        )

        if not prescription:
            return jsonify({'message': 'Failed to create prescription'}), 400

        return jsonify({
            'id': prescription.id,
            'patient_id': prescription.patient_id,
            'type': prescription.type,
            'description': prescription.description,
            'status': prescription.status
        }), 201

    @app.route('/prescriptions/<int:prescription_id>/complete', methods=['POST'])
    @token_required
    @role_required([UserRole.DOCTOR, UserRole.NURSE])
    def complete_prescription(current_user, prescription_id):
        prescription = db.complete_prescription(prescription_id, None, current_user.id)
        if not prescription:
            return jsonify({'message': 'Failed to complete prescription'}), 400

        return jsonify({'message': 'Prescription completed successfully'})

    @app.route('/patients/<int:patient_id>/prescriptions', methods=['GET'])
    @token_required
    @role_required([UserRole.DOCTOR, UserRole.NURSE])
    def get_patient_prescriptions(current_user, patient_id):
        prescriptions = db.get_patient_prescriptions(patient_id)
        return jsonify([{
            'id': p.id,
            'type': p.type,
            'description': p.description,
            'status': p.status,
            'assigned_to': p.assigned_to,
            'completion_date': p.completion_date.isoformat() if p.completion_date else None
        } for p in prescriptions])

if __name__ == '__main__':
    app.run(debug=True) 