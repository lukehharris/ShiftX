from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgres://lharris:binaans@localhost/shiftexchange')
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.setup_app(app)

app.secret_key = "DS53DFS2DF\SDF1SDF859DS5F2SD1F\2SD1F32SD1"

import shiftexchange.views

    