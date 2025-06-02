from enum import Enum

class UserRole(Enum):
    ADMIN = 'admin'
    DOCTOR = 'doctor'
    NURSE = 'nurse'
    PATIENT = 'patient'

class PrescriptionType(Enum):
    PROCEDURE = 'procedure'
    MEDICATION = 'medication'
    SURGERY = 'surgery' 