from flask import request, jsonify, Flask
from flask_restful import Resource, Api
from models import db, UserRole
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

    return jsonify(profile)

if __name__ == '__main__':
    app.run(debug=True) 
