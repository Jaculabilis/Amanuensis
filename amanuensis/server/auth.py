import time

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_login import current_user, login_user, logout_user, login_required

from amanuensis.config import logger, json_rw
from amanuensis.user import UserModel

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Stay logged in')
	submit = SubmitField('Log in')

def get_bp(login_manager):
	"""Create a blueprint for the auth functions"""
	bp = Blueprint('auth', __name__, url_prefix='/auth')

	@login_manager.user_loader
	def load_user(uid):
		return UserModel.by(uid=str(uid))

	@bp.route('/login/', methods=['GET', 'POST'])
	def login():
		form = LoginForm()
		if form.validate_on_submit():
			username = form.username.data
			u = UserModel.by(name=username)
			if u is not None and u.check_password(form.password.data):
				remember_me = form.remember.data
				login_user(u, remember=remember_me)
				with json_rw(u.config_path) as cfg:
					cfg.last_login = int(time.time())
				logger.info("Logged in user '{}' ({})".format(
					u.username, u.uid))
				return redirect(url_for('home.home'))
			flash("Login not recognized")
		return render_template('auth/login.html', form=form)

	@bp.route("/logout/", methods=['GET'])
	@login_required
	def logout():
		logout_user()
		return redirect(url_for('home.home'))

	return bp
