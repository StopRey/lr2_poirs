from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import bcrypt
import jwt
from models.enums.user_enums import UserRole
from models.database.hospital_db import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not all(k in data for k in ('username', 'password', 'role', 'name')):
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        role = UserRole(data['role'])
    except ValueError:
        return jsonify({'message': 'Invalid role'}), 400

    # Check if username already exists
    if db.users.get_user_by_username(data['username']):
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

    user = db.users.add_user(
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

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not all(k in data for k in ('username', 'password')):
        return jsonify({'message': 'Missing username or password'}), 400

    user = db.users.get_user_by_username(data['username'])
    if not user or not bcrypt.checkpw(data['password'].encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({'message': 'Invalid credentials'}), 401

    token = jwt.encode({
        'user_id': user['id'],
        'role': user['role'],
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, 'your-secret-key')  # TODO: Move to config

    return jsonify({
        'token': token,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'name': user['name']
        }
    }) 