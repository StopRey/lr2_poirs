from functools import wraps
from flask import request, jsonify
import jwt
from models.enums import UserRole
from . import app
from models.database.hospital_db import db

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.secret_key, algorithms=["HS256"])
            current_user = db.users.get_user(data['user_id'])
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