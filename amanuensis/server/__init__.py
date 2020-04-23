import os

from flask import Flask, render_template
from flask_login import LoginManager

from amanuensis.config import get, root
from amanuensis.server.auth import get_bp as get_auth_bp
from amanuensis.server.home import get_bp as get_home_bp
from amanuensis.server.helpers import register_custom_filters
from amanuensis.server.lexicon import get_bp as get_lex_bp
from amanuensis.user import AnonymousUserModel
from amanuensis.models import ModelFactory

# Flask app init
static_root = os.path.abspath(get("static_root"))
app = Flask(
	__name__,
	template_folder="../templates",
	static_folder=static_root)
app.secret_key = bytes.fromhex(get('secret_key'))
app.config['model_factory'] = ModelFactory(root)
app.jinja_options['trim_blocks'] = True
app.jinja_options['lstrip_blocks'] = True
register_custom_filters(app)

# Flask-Login init
login = LoginManager(app)
login.login_view = 'auth.login'
login.anonymous_user = AnonymousUserModel

# Blueprint inits
auth_bp = get_auth_bp(login)
app.register_blueprint(auth_bp)

home_bp = get_home_bp()
app.register_blueprint(home_bp)

lex_bp = get_lex_bp()
app.register_blueprint(lex_bp)
