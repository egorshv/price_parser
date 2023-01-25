import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
TOKEN = '5855610205:AAGG8pruRmDe2lWZzszN4y-aXiF1QvB4RZk'

db = SQLAlchemy(app)

login_manager = LoginManager(app)
