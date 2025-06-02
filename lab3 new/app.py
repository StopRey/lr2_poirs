from flask import Flask, jsonify
from routes import auth_bp, profile_bp, patient_bp, prescription_bp

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # TODO: Move to config

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(profile_bp, url_prefix='/profile')
app.register_blueprint(patient_bp, url_prefix='/patient')
app.register_blueprint(prescription_bp, url_prefix='/prescription')

@app.route('/')
def index():
    return jsonify({
        'message': 'Hospital Management System API',
        'endpoints': {
            'auth': {
                'register': '/auth/register',
                'login': '/auth/login'
            },
            'profile': {
                'get_profile': '/profile/profile',
                'get_all_users': '/profile/users'
            },
            'patient': {
                'update_diagnosis': '/patient/patients/<id>/diagnosis',
                'discharge': '/patient/patients/<id>/discharge'
            },
            'prescription': {
                'create': '/prescription/prescriptions',
                'complete': '/prescription/prescriptions/<id>/complete',
                'get_patient_prescriptions': '/prescription/patients/<id>/prescriptions'
            }
        }
    })

if __name__ == '__main__':
    app.run(debug=True)