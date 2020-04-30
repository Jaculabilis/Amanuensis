from flask_wtf import FlaskForm
from wtforms import (
	StringField, SubmitField, TextAreaField, RadioField)
from wtforms.validators import DataRequired

from .settings import ConfigFormBase


class LexiconCharacterForm(FlaskForm):
	"""/lexicon/<name>/session/character/"""
	characterName = StringField(
		'Character name',
		validators=[DataRequired()])
	defaultSignature = TextAreaField('Default signature')
	submit = SubmitField('Submit')

	def for_new(self):
		self.characterName.data = ""
		self.defaultSignature.data = "~"
		return self

	def for_character(self, character):
		self.characterName.data = character.name
		self.defaultSignature.data = character.signature
		return self


class LexiconReviewForm(FlaskForm):
	"""/lexicon/<name>/session/review/"""
	APPROVED = 'Y'
	REJECTED = 'N'
	approved = RadioField(
		'Buttons',
		choices=((APPROVED, 'Approved'), (REJECTED, 'Rejected')))
	submit = SubmitField("Submit")


class LexiconPublishTurnForm(FlaskForm):
	"""/lexicon/<name>/session/"""
	submit = SubmitField('Publish turn')


class LexiconConfigForm(ConfigFormBase):
	"""/lexicon/<name>/session/settings/"""
	submit = SubmitField('Save settings')
