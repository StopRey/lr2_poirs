from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    NURSE = "nurse"

@dataclass
class User:
    id: int
    username: str
    password_hash: str
    role: UserRole
    name: str
    is_active: bool = True

@dataclass
class Patient:
    id: int
    name: str
    admission_date: datetime
    discharge_date: Optional[datetime] = None
    final_diagnosis: Optional[str] = None
    current_diagnosis: Optional[str] = None
    prescriptions: List['Prescription'] = None
    assigned_doctor_id: Optional[int] = None

    def __post_init__(self):
        if self.prescriptions is None:
            self.prescriptions = []

@dataclass
class Doctor:
    id: int
    name: str
    specialization: str
    user_id: Optional[int] = None

@dataclass
class Nurse:
    id: int
    name: str
    user_id: Optional[int] = None

@dataclass
class Prescription:
    id: int
    patient_id: int
    doctor_id: int
    type: str  # 'procedure', 'medicine', 'surgery'
    description: str
    status: str  # 'pending', 'completed'
    assigned_to: str  # 'doctor' or 'nurse'
    completed_by: Optional[int] = None  # ID of doctor or nurse who completed it
    completion_date: Optional[datetime] = None 