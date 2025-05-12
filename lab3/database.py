from typing import Dict, List, Optional
from datetime import datetime
from models import Patient, Doctor, Nurse, Prescription, User, UserRole
import bcrypt

class Database:
    def __init__(self):
        self.patients: Dict[int, Patient] = {}
        self.doctors: Dict[int, Doctor] = {}
        self.nurses: Dict[int, Nurse] = {}
        self.prescriptions: Dict[int, Prescription] = {}
        self.users: Dict[int, User] = {}
        self._next_patient_id = 1
        self._next_doctor_id = 1
        self._next_nurse_id = 1
        self._next_prescription_id = 1
        self._next_user_id = 1

    # User operations
    def add_user(self, username: str, password: str, role: UserRole, name: str) -> User:
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = User(
            id=self._next_user_id,
            username=username,
            password_hash=password_hash,
            role=role,
            name=name
        )
        self.users[user.id] = user
        self._next_user_id += 1
        return user

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        for user in self.users.values():
            if user.username == username and bcrypt.checkpw(password.encode('utf-8'), user.password_hash):
                return user
        return None

    def get_user(self, user_id: int) -> Optional[User]:
        return self.users.get(user_id)

    # Patient operations
    def add_patient(self, name: str, assigned_doctor_id: Optional[int] = None) -> Patient:
        patient = Patient(
            id=self._next_patient_id,
            name=name,
            admission_date=datetime.now(),
            assigned_doctor_id=assigned_doctor_id
        )
        self.patients[patient.id] = patient
        self._next_patient_id += 1
        return patient

    def get_patient(self, patient_id: int) -> Optional[Patient]:
        return self.patients.get(patient_id)

    def update_patient(self, patient: Patient) -> None:
        self.patients[patient.id] = patient

    def discharge_patient(self, patient_id: int, final_diagnosis: str, doctor_id: int) -> Optional[Patient]:
        patient = self.get_patient(patient_id)
        doctor = self.get_doctor(doctor_id)
        if patient and doctor and doctor.user_id:
            patient.discharge_date = datetime.now()
            patient.final_diagnosis = final_diagnosis
            self.update_patient(patient)
        return patient

    # Doctor operations
    def add_doctor(self, name: str, specialization: str, user_id: Optional[int] = None) -> Doctor:
        doctor = Doctor(
            id=self._next_doctor_id,
            name=name,
            specialization=specialization,
            user_id=user_id
        )
        self.doctors[doctor.id] = doctor
        self._next_doctor_id += 1
        return doctor

    def get_doctor(self, doctor_id: int) -> Optional[Doctor]:
        return self.doctors.get(doctor_id)

    def get_doctor_by_user_id(self, user_id: int) -> Optional[Doctor]:
        for doctor in self.doctors.values():
            if doctor.user_id == user_id:
                return doctor
        return None

    # Nurse operations
    def add_nurse(self, name: str, user_id: Optional[int] = None) -> Nurse:
        nurse = Nurse(
            id=self._next_nurse_id,
            name=name,
            user_id=user_id
        )
        self.nurses[nurse.id] = nurse
        self._next_nurse_id += 1
        return nurse

    def get_nurse(self, nurse_id: int) -> Optional[Nurse]:
        return self.nurses.get(nurse_id)

    def get_nurse_by_user_id(self, user_id: int) -> Optional[Nurse]:
        for nurse in self.nurses.values():
            if nurse.user_id == user_id:
                return nurse
        return None

    # Prescription operations
    def add_prescription(self, patient_id: int, doctor_id: int, 
                        type: str, description: str, assigned_to: str) -> Optional[Prescription]:
        if patient_id not in self.patients or doctor_id not in self.doctors:
            return None

        prescription = Prescription(
            id=self._next_prescription_id,
            patient_id=patient_id,
            doctor_id=doctor_id,
            type=type,
            description=description,
            status='pending',
            assigned_to=assigned_to
        )
        self.prescriptions[prescription.id] = prescription
        self.patients[patient_id].prescriptions.append(prescription)
        self._next_prescription_id += 1
        return prescription

    def complete_prescription(self, prescription_id: int, completed_by_id: int, user_id: int) -> Optional[Prescription]:
        prescription = self.prescriptions.get(prescription_id)
        if not prescription or prescription.status == 'completed':
            return None

        user = self.get_user(user_id)
        if not user:
            return None

        # Check if user has permission to complete this prescription
        if user.role == UserRole.DOCTOR:
            doctor = self.get_doctor_by_user_id(user_id)
            if not doctor:
                return None
            prescription.completed_by = doctor.id
        elif user.role == UserRole.NURSE:
            nurse = self.get_nurse_by_user_id(user_id)
            if not nurse or prescription.type == 'surgery':
                return None
            prescription.completed_by = nurse.id
        else:
            return None

        prescription.status = 'completed'
        prescription.completion_date = datetime.now()
        return prescription

    def get_patient_prescriptions(self, patient_id: int) -> List[Prescription]:
        patient = self.get_patient(patient_id)
        return patient.prescriptions if patient else []

# Create a global database instance
db = Database() 