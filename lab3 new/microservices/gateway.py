from flask import Flask, jsonify, request, redirect
import requests

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # TODO: Move to config

# Service URLs
SERVICES = {
    'auth': 'http://localhost:5001',
    'profile': 'http://localhost:5002',
    'patient': 'http://localhost:5003',
    'prescription': 'http://localhost:5004'
}

def forward_request(service_name, path):
    """Forward the request to the appropriate service"""
    if service_name not in SERVICES:
        return jsonify({'error': 'Service not found'}), 404
    
    service_url = SERVICES[service_name]
    target_url = f"{service_url}{path}"
    
    # Forward the request with the same method and data
    response = requests.request(
        method=request.method,
        url=target_url,
        headers={key: value for key, value in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False
    )
    
    return response.content, response.status_code, response.headers.items()

# Route for auth service
@app.route('/auth/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def auth_service(path):
    return forward_request('auth', f'/auth/{path}')

# Route for profile service
@app.route('/profile/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def profile_service(path):
    return forward_request('profile', f'/profile/{path}')

# Route for patient service
@app.route('/patient/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def patient_service(path):
    return forward_request('patient', f'/patient/{path}')

# Route for prescription service
@app.route('/prescription/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def prescription_service(path):
    return forward_request('prescription', f'/prescription/{path}')

@app.route('/')
def index():
    return jsonify({
        'message': 'Hospital Management System API Gateway',
        'services': {
            'auth': {
                'url': SERVICES['auth'],
                'endpoints': {
                    'register': '/auth/register',
                    'login': '/auth/login'
                }
            },
            'profile': {
                'url': SERVICES['profile'],
                'endpoints': {
                    'get_profile': '/profile/profile',
                    'get_all_users': '/profile/users'
                }
            },
            'patient': {
                'url': SERVICES['patient'],
                'endpoints': {
                    'update_diagnosis': '/patient/patients/<id>/diagnosis',
                    'discharge': '/patient/patients/<id>/discharge'
                }
            },
            'prescription': {
                'url': SERVICES['prescription'],
                'endpoints': {
                    'create': '/prescription/prescriptions',
                    'complete': '/prescription/prescriptions/<id>/complete',
                    'get_patient_prescriptions': '/prescription/patients/<id>/prescriptions'
                }
            }
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000) 