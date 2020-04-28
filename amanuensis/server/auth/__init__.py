import logging
import time

from flask import (
	Blueprint,
	render_template,
	redirect,
	url_for,
	flash,
	current_app)
from flask_login import (
	login_user,
	logout_user,
	login_required,
	LoginManager)

from amanuensis.config import RootConfigDirectoryContext
from amanuensis.models import ModelFactory, AnonymousUserModel

from .forms import LoginForm

logger = logging.getLogger(__name__)


def get_login_manager(root: RootConfigDirectoryContext) -> LoginManager:
	"""
	Creates a login manager
	"""
	login_manager = LoginManager()
	login_manager.login_view = 'auth.login'
	login_manager.anonymous_user = AnonymousUserModel

	@login_manager.user_loader
	def load_user(uid):
		return current_app.config['model_factory'].user(str(uid))

	return login_manager


bp_auth = Blueprint('auth', __name__,
	url_prefix='/auth',
	template_folder='.')


@bp_auth.route('/login/', methods=['GET', 'POST'])
def login():
	model_factory: ModelFactory = current_app.config['model_factory']
	form = LoginForm()

	if not form.validate_on_submit():
		# Either the request was GET and we should render the form,
		# or the request was POST and validation failed.
		return render_template('auth.login.jinja', form=form)

	# POST with valid data
	username = form.username.data
	user = model_factory.try_user(username)
	if not user or not user.check_password(form.password.data):
		# Bad creds
		flash("Login not recognized")
		return redirect(url_for('auth.login'))

	# Login credentials were correct
	remember_me = form.remember.data
	login_user(user, remember=remember_me)
	with user.ctx.edit_config() as cfg:
		cfg.last_login = int(time.time())
	logger.info('Logged in user "{0.username}" ({0.uid})'.format(user.cfg))
	return redirect(url_for('home.home'))


@bp_auth.route("/logout/", methods=['GET'])
@login_required
def logout():
	logout_user()
	return redirect(url_for('home.home'))
