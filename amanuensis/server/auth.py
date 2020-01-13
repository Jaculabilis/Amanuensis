import flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_login import current_user, login_user

import config
import user

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	#password = PasswordField('Password', validators=[DataRequired()])
	#remember = BooleanField('Remember Me')
	submit = SubmitField('Log in')

def get_bp(login_manager):
	"""Create a blueprint for the auth functions"""
	bp = flask.Blueprint('auth', __name__, url_prefix='/auth')

	@login_manager.user_loader
	def load_user(uid):
		return user.user_from_uid(str(uid))

	@bp.route('/login/', methods=['GET', 'POST'])
	def login():
		form = LoginForm()
		if form.validate_on_submit():
			username = form.username.data
			uid = user.uid_from_username(username)
			if uid is None:
				pass
			u = user.user_from_uid(uid)
			login_user(u)
			config.logger.info("Logged in user '{}' ({})".format(u.get('username'), u.uid))
			name = u.get('username')
		else:
			name = "guest"
		return flask.render_template('auth/login.html', form=form, username=name)

	return bp
