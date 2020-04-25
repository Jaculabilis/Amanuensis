from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

from amanuensis.server.forms import User


class LoginForm(FlaskForm):
	"""/auth/login/"""
	username = StringField(
		'Username',
		validators=[DataRequired(), User()])
	password = PasswordField(
		'Password',
		validators=[DataRequired()])
	remember = BooleanField('Stay logged in')
	submit = SubmitField('Log in')
