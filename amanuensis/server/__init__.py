from flask import Flask, render_template
from flask_login import LoginManager

import config
from server.auth import get_bp as get_auth_bp

app = Flask(__name__, template_folder="../templates")
app.secret_key = bytes.fromhex(config.get('secret_key'))
login = LoginManager(app)
auth_bp = get_auth_bp(login)
app.register_blueprint(auth_bp)

