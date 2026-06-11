from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import os
import secrets

import logging

app = Flask(__name__)
<<<<<<< HEAD

app.config['SECRET_KEY'] = '45cf93c4d41348cd9980674ade9a7356'
=======
# Load SECRET_KEY from environment in production. If not set, generate
# an ephemeral key for development/testing to avoid hardcoding secrets.
secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
	# Generate a random key if none provided (not suitable for production)
	secret_key = secrets.token_hex(32)
	app.logger.warning('SECRET_KEY not set in environment; using ephemeral key')

app.config['SECRET_KEY'] = secret_key
>>>>>>> develop
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'danger'

bcrypt = Bcrypt(app)

# Configuração de Logs
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

app.logger.setLevel(logging.INFO)

# Always put Routes at end
from todo_project import routes
