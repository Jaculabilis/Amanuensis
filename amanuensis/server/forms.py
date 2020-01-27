from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError

from amanuensis.config import json_ro


# Custom validators
def user(exists=True):
	template = 'User "{{}}" {}'.format("not found" if exists else "already exists")
	should_exist = bool(exists)
	def validate_user(form, field):
		with json_ro('user', 'index.json') as index:
			if (field.data in index.keys()) != should_exist:
				raise ValidationError(template.format(field.data))
	return validate_user


def lexicon(exists=True):
	template = 'Lexicon "{{}}" {}'.format("not found" if exists else "already exists")
	should_exist = bool(exists)
	def validate_lexicon(form, field):
		with json_ro('lexicon', 'index.json') as index:
			if (field.data in index.keys()) != should_exist:
				raise ValidationError(template.format(field.data))
	return validate_lexicon


# Forms
class LoginForm(FlaskForm):
	"""/auth/login/"""
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Stay logged in')
	submit = SubmitField('Log in')


class LexiconCreateForm(FlaskForm):
	"""/admin/create/"""
	lexiconName = StringField('Lexicon name', validators=[DataRequired(), lexicon(exists=False)])
	editorName = StringField('Username of editor', validators=[DataRequired(), user(exists=True)])
	promptText = TextAreaField("Prompt")
	submit = SubmitField('Create')


class LexiconConfigForm(FlaskForm):
	"""/lexicon/<name>/session/settings/"""
	configText = TextAreaField("Config file")
	submit = SubmitField("Submit")