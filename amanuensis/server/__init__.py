import os

from flask import Flask, render_template
from flask_login import LoginManager

import config
from server.auth import get_bp as get_auth_bp
from server.home import get_bp as get_home_bp

# Flask app init
static_root = os.path.abspath(config.get("static_root"))
app = Flask(__name__, template_folder="../templates", static_folder=static_root)
app.secret_key = bytes.fromhex(config.get('secret_key'))

# Flask-Login init
login = LoginManager(app)
login.login_view = 'auth.login'

# Blueprint inits
auth_bp = get_auth_bp(login)
app.register_blueprint(auth_bp)

home_bp = get_home_bp()
app.register_blueprint(home_bp)
