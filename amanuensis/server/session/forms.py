from flask_wtf import FlaskForm
from wtforms import (
	StringField, SubmitField, TextAreaField, RadioField)
from wtforms.validators import DataRequired

from amanuensis.lexicon import create_character_in_lexicon


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

	def for_character(self, lexicon, cid):
		char = lexicon.cfg.character.get(cid)
		self.characterName.data = char.name
		self.defaultSignature.data = char.signature

	def add_character(self, lexicon, user):
		create_character_in_lexicon(user, lexicon, self.characterName.data)
		# add_character(lexicon, user, {
		# 	'name': self.characterName.data,
		# 	'signature': self.defaultSignature.data,
		# })

	def update_character(self, lexicon, cid):
		with lexicon.ctx.edit_config() as cfg:
			char = cfg.character.get(cid)
			char.name = self.characterName.data
			char.signature = self.defaultSignature.data


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
