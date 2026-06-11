from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import os
import secrets


app = Flask(__name__)
# Load SECRET_KEY from environment in production. If not set, generate
# an ephemeral key for development/testing to avoid hardcoding secrets.
secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
	# Generate a random key if none provided (not suitable for production)
	secret_key = secrets.token_hex(32)
	app.logger.warning('SECRET_KEY not set in environment; using ephemeral key')

app.config['SECRET_KEY'] = secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'danger'

bcrypt = Bcrypt(app)

# Always put Routes at end
from todo_project import routes