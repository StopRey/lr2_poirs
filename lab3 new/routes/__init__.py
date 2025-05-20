from flask import Flask
from flask_restful import Api

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this to a secure secret key in production
api = Api(app)

from .auth_routes import *
from .profile_routes import *
from .patient_routes import *
from .prescription_routes import * 