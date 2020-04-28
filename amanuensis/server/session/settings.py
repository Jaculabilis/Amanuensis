from flask_wtf import FlaskForm
from wtforms import (
	StringField, BooleanField, SubmitField, TextAreaField,
	IntegerField, SelectField)
from wtforms.validators import DataRequired, ValidationError, Optional
from wtforms.widgets.html5 import NumberInput

from amanuensis.server.forms import User


class LexiconConfigForm(FlaskForm):
	"""/lexicon/<name>/session/settings/"""
	# General
	title = StringField('Title override', validators=[Optional()])
	editor = SelectField('Editor', validators=[DataRequired(), User(True)])
	prompt = TextAreaField('Prompt', validators=[DataRequired()])
	# Turn
	turnCurrent = IntegerField('Current turn', widget=NumberInput(), validators=[Optional()])
	turnMax = IntegerField('Number of turns', widget=NumberInput(), validators=[DataRequired()])
	# Join
	joinPublic = BooleanField("Show game on public pages")
	joinOpen = BooleanField("Allow players to join game")
	joinPassword = StringField("Password to join game", validators=[Optional()])
	joinMaxPlayers = IntegerField(
		"Maximum number of players",
		widget=NumberInput(),
		validators=[DataRequired()])
	joinCharsPerPlayer = IntegerField(
		"Characters per player",
		widget=NumberInput(),
		validators=[DataRequired()])
	# Publish
	publishNotifyEditorOnReady = BooleanField(
		"Notify the editor when a player marks an article as ready")
	publishNotifyPlayerOnReject = BooleanField(
		"Notify a player when their article is rejected by the editor")
	publishNotifyPlayerOnAccept = BooleanField(
		"Notify a player when their article is accepted by the editor")
	publishDeadlines = StringField(
		"Turn deadline, as a crontab specification", validators=[Optional()])
	publishAsap = BooleanField(
		"Publish the turn immediately when the last article is accepted")
	publishQuorum = IntegerField(
		"Quorum to publish incomplete turn", widget=NumberInput(), validators=[Optional()])
	publishBlockOnReady = BooleanField(
		"Block turn publish if any articles are awaiting editor review")
	# Article
	articleIndexList = TextAreaField("Index specifications")
	articleIndexCapacity = IntegerField(
		"Index capacity override", widget=NumberInput(), validators=[Optional()])
	articleCitationAllowSelf = BooleanField(
		"Allow players to cite themselves")
	articleCitationMinExtant = IntegerField(
		"Minimum number of extant articles to cite", widget=NumberInput(), validators=[Optional()])
	articleCitationMaxExtant = IntegerField(
		"Maximum number of extant articles to cite", widget=NumberInput(), validators=[Optional()])
	articleCitationMinPhantom = IntegerField(
		"Minimum number of phantom articles to cite", widget=NumberInput(), validators=[Optional()])
	articleCitationMaxPhantom = IntegerField(
		"Maximum number of phantom articles to cite", widget=NumberInput(), validators=[Optional()])
	articleCitationMinTotal = IntegerField(
		"Minimum number of articles to cite in total", widget=NumberInput(), validators=[Optional()])
	articleCitationMaxTotal = IntegerField(
		"Maximum number of articles to cite in total", widget=NumberInput(), validators=[Optional()])
	articleCitationMinChars = IntegerField(
		"Minimum number of characters to cite articles by",
		widget=NumberInput(), validators=[Optional()])
	articleCitationMaxChars = IntegerField(
		"Maximum number of characters to cite articles by",
		widget=NumberInput(), validators=[Optional()])
	articleWordLimitSoft = IntegerField(
		"Soft word limit", widget=NumberInput(), validators=[Optional()])
	articleWordLimitHard = IntegerField(
		"Hard word limit", widget=NumberInput(), validators=[Optional()])
	articleAddendumAllowed = BooleanField("Allow addendum articles")
	articleAddendumMax = IntegerField(
		"Maximum number of addendum articles per character per turn",
		widget=NumberInput(), validators=[Optional()])
	# And finally, the submit button
	submit = SubmitField("Submit")

	def validate_publishDeadlines(form, field):
		if form.publishAsap.data:
			raise ValidationError('Cannot specify deadline if immediate publishing is enabled')

	# TODO add validators that call into extant valid check methods

	# def set_options(self, lexicon):
	# 	self.editor.choices = list(map(lambda x: (x, x), map(
	# 		lambda uid: UserModel.by(uid=uid).username,
	# 		lexicon.join.joined)))

	# def populate_from_lexicon(self, lexicon):
	# 	self.title.data = lexicon.cfg.title
	# 	self.editor.data = ModelFactory(lexicon.ctx.root).user(lexicon.cfg.editor).cfg.username
	# 	self.prompt.data = lexicon.prompt
	# 	self.turnCurrent.data = lexicon.turn.current
	# 	self.turnMax.data = lexicon.turn.max
	# 	self.joinPublic.data = lexicon.join.public
	# 	self.joinOpen.data = lexicon.join.open
	# 	self.joinPassword.data = lexicon.join.password
	# 	self.joinMaxPlayers.data = lexicon.join.max_players
	# 	self.joinCharsPerPlayer.data = lexicon.join.chars_per_player
	# 	self.publishNotifyEditorOnReady.data = lexicon.publish.notify.editor_on_ready
	# 	self.publishNotifyPlayerOnReject.data = lexicon.publish.notify.player_on_reject
	# 	self.publishNotifyPlayerOnAccept.data = lexicon.publish.notify.player_on_accept
	# 	self.publishDeadlines.data = lexicon.publish.deadlines
	# 	self.publishAsap.data = lexicon.publish.asap
	# 	self.publishQuorum.data = lexicon.publish.quorum
	# 	self.publishBlockOnReady.data = lexicon.publish.block_on_ready
	# 	self.articleIndexList.data = lexicon.article.index.list
	# 	self.articleIndexCapacity.data = lexicon.article.index.capacity
	# 	self.articleCitationAllowSelf.data = lexicon.article.citation.allow_self
	# 	self.articleCitationMinExtant.data = lexicon.article.citation.min_extant
	# 	self.articleCitationMaxExtant.data = lexicon.article.citation.max_extant
	# 	self.articleCitationMinPhantom.data = lexicon.article.citation.min_phantom
	# 	self.articleCitationMaxPhantom.data = lexicon.article.citation.max_phantom
	# 	self.articleCitationMinTotal.data = lexicon.article.citation.min_total
	# 	self.articleCitationMaxTotal.data = lexicon.article.citation.max_total
	# 	self.articleCitationMinChars.data = lexicon.article.citation.min_chars
	# 	self.articleCitationMaxChars.data = lexicon.article.citation.max_chars
	# 	self.articleWordLimitSoft.data = lexicon.article.word_limit.soft
	# 	self.articleWordLimitHard.data = lexicon.article.word_limit.hard
	# 	self.articleAddendumAllowed.data = lexicon.article.addendum.allowed
	# 	self.articleAddendumMax.data = lexicon.article.addendum.max

	# def update_lexicon(self, lexicon):
	# 	with lexicon.edit() as l:
	# 		l.title = self.title.data
	# 		l.editor = UserModel.by(name=self.editor.data).uid
	# 		l.prompt = self.prompt.data
	# 		l.turn.current = self.turnCurrent.data
	# 		l.turn.max = self.turnMax.data
	# 		l.join.public = self.joinPublic.data
	# 		l.join.open = self.joinOpen.data
	# 		l.join.password = self.joinPassword.data
	# 		l.join.max_players = self.joinMaxPlayers.data
	# 		l.join.chars_per_player = self.joinCharsPerPlayer.data
	# 		l.publish.notify.editor_on_ready = self.publishNotifyEditorOnReady.data
	# 		l.publish.notify.player_on_reject = self.publishNotifyPlayerOnReject.data
	# 		l.publish.notify.player_on_accept = self.publishNotifyPlayerOnAccept.data
	# 		l.publish.deadlines = self.publishDeadlines.data
	# 		l.publish.asap = self.publishAsap.data
	# 		l.publish.quorum = self.publishQuorum.data
	# 		l.publish.block_on_ready = self.publishBlockOnReady.data
	# 		l.article.index.list = self.articleIndexList.data
	# 		l.article.index.capacity = self.articleIndexCapacity.data
	# 		l.article.citation.allow_self = self.articleCitationAllowSelf.data
	# 		l.article.citation.min_extant = self.articleCitationMinExtant.data
	# 		l.article.citation.max_extant = self.articleCitationMaxExtant.data
	# 		l.article.citation.min_phantom = self.articleCitationMinPhantom.data
	# 		l.article.citation.max_phantom = self.articleCitationMaxPhantom.data
	# 		l.article.citation.min_total = self.articleCitationMinTotal.data
	# 		l.article.citation.max_total = self.articleCitationMaxTotal.data
	# 		l.article.citation.min_chars = self.articleCitationMinChars.data
	# 		l.article.citation.max_chars = self.articleCitationMaxChars.data
	# 		l.article.word_limit.soft = self.articleWordLimitSoft.data
	# 		l.article.word_limit.hard = self.articleWordLimitHard.data
	# 		l.article.addendum.allowed = self.articleAddendumAllowed.data
	# 		l.article.addendum.max = self.articleAddendumMax.data
	# 	return True
