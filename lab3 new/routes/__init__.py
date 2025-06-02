from flask import Blueprint
from .auth import auth_bp
from .profile import profile_bp
from .patient import patient_bp
from .prescription import prescription_bp
from .common import token_required, role_required

__all__ = [
    'auth_bp',
    'profile_bp',
    'patient_bp',
    'prescription_bp',
    'token_required',
    'role_required'
] 