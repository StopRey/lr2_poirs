import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify
from routes.prescription import prescription_bp

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # TODO: Move to config

# Register prescription blueprint
app.register_blueprint(prescription_bp, url_prefix='/prescription')

@app.route('/')
def index():
    return jsonify({
        'service': 'Prescription Service',
        'endpoints': {
            'create': '/prescription/prescriptions',
            'complete': '/prescription/prescriptions/<id>/complete',
            'get_patient_prescriptions': '/prescription/patients/<id>/prescriptions'
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5004) 