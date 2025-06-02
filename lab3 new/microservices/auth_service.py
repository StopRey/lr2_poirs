import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify
from routes.auth import auth_bp

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # TODO: Move to config

# Register auth blueprint
app.register_blueprint(auth_bp, url_prefix='/auth')

@app.route('/')
def index():
    return jsonify({
        'service': 'Auth Service',
        'endpoints': {
            'register': '/auth/register',
            'login': '/auth/login'
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001) 