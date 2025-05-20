from .base import Database
from .user_manager import UserManager
from .patient_manager import PatientManager
from .prescription_manager import PrescriptionManager

class HospitalDatabase:
    def __init__(self, db_name='hospital.db'):
        self.db = Database(db_name)
        self.users = UserManager(self)
        self.patients = PatientManager(self)
        self.prescriptions = PrescriptionManager(self)

db = HospitalDatabase()