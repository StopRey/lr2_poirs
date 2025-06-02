import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify
from routes.patient import patient_bp

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # TODO: Move to config

# Register patient blueprint
app.register_blueprint(patient_bp, url_prefix='/patient')

@app.route('/')
def index():
    return jsonify({
        'service': 'Patient Service',
        'endpoints': {
            'update_diagnosis': '/patient/patients/<id>/diagnosis',
            'discharge': '/patient/patients/<id>/discharge'
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5003) 