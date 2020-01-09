from flask import Flask, render_template

import config

app = Flask(__name__, template_folder="../templates")
app.secret_key = bytes.fromhex(config.get('secret_key'))

from .auth import bp
app.register_blueprint(auth.bp)

