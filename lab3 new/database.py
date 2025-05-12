from models import db, User, Doctor, Nurse, Patient, UserRole
import bcrypt
from datetime import datetime

class Database:
    def __init__(self, app):
        self.app = app
        with app.app_context():
            db.create_all()

    def add_user(self, username, password, role, name, **kwargs):
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Create user
        user = User(
            username=username,
            password=hashed_password.decode('utf-8'),
            role=role,
            name=name
        )
        db.session.add(user)
        db.session.flush()  # Get the user ID without committing

        # Create role-specific record
        if role == UserRole.DOCTOR:
            doctor = Doctor(
                user_id=user.id,
                specialization=kwargs.get('specialization', '')
            )
            db.session.add(doctor)
        elif role == UserRole.NURSE:
            nurse = Nurse(
                user_id=user.id,
                department=kwargs.get('department', '')
            )
            db.session.add(nurse)
        elif role == UserRole.PATIENT:
            patient = Patient(
                user_id=user.id,
                doctor_id=kwargs.get('doctor_id')
            )
            db.session.add(patient)

        db.session.commit()
        return user

    def get_user(self, user_id):
        return User.query.get(user_id)

    def get_user_by_username(self, username):
        return User.query.filter_by(username=username).first()

    def authenticate_user(self, username, password):
        user = self.get_user_by_username(username)
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return user
        return None

    def get_doctor_by_user_id(self, user_id):
        return Doctor.query.filter_by(user_id=user_id).first()

    def get_nurse_by_user_id(self, user_id):
        return Nurse.query.filter_by(user_id=user_id).first()

    def get_patient_by_user_id(self, user_id):
        return Patient.query.filter_by(user_id=user_id).first()

    def get_patient(self, patient_id):
        return Patient.query.get(patient_id)

    def update_patient(self, patient):
        db.session.commit()
        return patient

    def discharge_patient(self, patient_id, final_diagnosis):
        patient = self.get_patient(patient_id)
        if patient:
            patient.discharge_date = datetime.utcnow()
            patient.final_diagnosis = final_diagnosis
            db.session.commit()
        return patient 