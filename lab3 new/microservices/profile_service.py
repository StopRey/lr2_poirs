import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify
from routes.profile import profile_bp

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # TODO: Move to config

# Register profile blueprint
app.register_blueprint(profile_bp, url_prefix='/profile')

@app.route('/')
def index():
    return jsonify({
        'service': 'Profile Service',
        'endpoints': {
            'get_profile': '/profile/profile',
            'get_all_users': '/profile/users'
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5002) 