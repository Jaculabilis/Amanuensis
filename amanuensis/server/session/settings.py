import re
from typing import cast

from flask import current_app
from flask_wtf import FlaskForm
from wtforms import (
	Field,
	StringField,
	BooleanField,
	TextAreaField,
	IntegerField,
	SelectField,
	ValidationError)
from wtforms.validators import DataRequired, Optional
from wtforms.widgets.html5 import NumberInput

from amanuensis.config import ReadOnlyOrderedDict, AttrOrderedDict
from amanuensis.models import ModelFactory, UserModel
from amanuensis.server.forms import User


index_regex = re.compile(
	r'(char|prefix|etc)'  # index type
	r'(\[(-?\d+)\])?'     # index pri
	r':(.+)')             # index pattern


class SettingTranslator():
	"""
	Base class for the translation layer between internal config data
	and user-friendly display in the settings form. By default the data
	is returned as-is.
	"""
	def load(self, cfg_value):
		return cfg_value

	def save(self, field_data):
		return field_data


class UsernameTranslator(SettingTranslator):
	"""
	Converts an internal user id to a public-facing username.
	"""
	def load(self, cfg_value):
		model_factory: ModelFactory = current_app.config['model_factory']
		user: UserModel = model_factory.user(cfg_value)
		return user.cfg.username

	def save(self, field_data):
		model_factory: ModelFactory = current_app.config['model_factory']
		user: UserModel = model_factory.try_user(field_data)
		if user:
			return user.uid


class IndexListTranslator(SettingTranslator):
	"""
	Converts internal index representations into the index
	specification format used in the editable list.
	"""
	def load(self, cfg_value):
		index_list = []
		for index in cfg_value:
			if index.pri == 0:
				index_list.append('{type}:{pattern}'.format(**index))
			else:
				index_list.append('{type}[{pri}]:{pattern}'.format(**index))
		return '\n'.join(index_list)

	def save(self, field_data):
		index_list = []
		has_etc = False
		for index in field_data.split('\n'):
			match = index_regex.fullmatch(index)
			itype, _, pri, pattern = match.groups()
			index_list.append(dict(
				type=itype,
				pri=pri or 0,
				pattern=pattern.strip()))
			if itype == 'etc':
				has_etc = True
		if not has_etc:
			index_list.append(dict(
				type='etc',
				pri=0,
				pattern='&c'))
		return index_list


class Setting():
	"""
	Represents a relation between a node in a lexicon config and a
	field in a public-facing form that exposes it to the editor for
	modification.
	"""
	def __init__(
		self,
		cfg_key: str,
		field: Field,
		translator: SettingTranslator = SettingTranslator()):
		"""
		Creates a setting. Optionally, defines a nontrivial translation
		between internal and public values.
		"""
		self.cfg_path = cfg_key.split('.')
		self.field = field
		self.translator = translator

	def load(self, cfg: ReadOnlyOrderedDict, field: Field):
		"""
		Sets the field's value to the corresponding config node
		"""
		for key in self.cfg_path[:-1]:
			cfg = cast(ReadOnlyOrderedDict, cfg.get(key))
		data = cfg.get(self.cfg_path[-1])
		field.data = self.translator.load(data)

	def save(self, cfg: AttrOrderedDict, field: Field):
		"""
		Updates the editable config with this field's value
		"""
		for key in self.cfg_path[:-1]:
			cfg = cast(AttrOrderedDict, cfg.get(key))
		data = field.data
		cfg[self.cfg_path[-1]] = self.translator.save(data)


def IndexList(form, field):
	if not field.data:
		raise ValidationError('You must specify an index list.')
	etc_count = 0
	for index in field.data.split('\n'):
		match = index_regex.fullmatch(index)
		if not match:
			raise ValidationError(f'Bad index: "{index}"')
		if match.group(1) == 'etc':
			etc_count += 1
	if etc_count > 1:
		raise ValidationError("Can't have more than one etc index")


class Settings():
	@staticmethod
	def settings():
		for name, setting in vars(Settings).items():
			if name.startswith('s_'):
				yield name, setting

	s_title = Setting('title',
		StringField('Title override', validators=[Optional()]))

	s_editor = Setting('editor',
		SelectField('Editor', validators=[DataRequired(), User(True)]),
		translator=UsernameTranslator())

	s_prompt = Setting('prompt',
		TextAreaField('Prompt', validators=[DataRequired()]))

	s_turnCurrent = Setting('turn.current',
		IntegerField(
			'Current turn',
			widget=NumberInput(),
			validators=[Optional()]))

	s_turnMax = Setting('turn.max',
		IntegerField(
			'Number of turns',
			widget=NumberInput(),
			validators=[DataRequired()]))

	s_joinPublic = Setting('join.public',
		BooleanField('Show game on public pages'))

	s_joinOpen = Setting('join.open',
		BooleanField('Allow players to join game'))

	s_joinPassword = Setting('join.password',
		StringField('Password to join game', validators=[Optional()]))

	s_joinMaxPlayers = Setting('join.max_players',
		IntegerField(
			'Maximum number of players',
			widget=NumberInput(),
			validators=[DataRequired()]))

	s_joinCharsPerPlayer = Setting('join.chars_per_player',
		IntegerField(
			'Characters per player',
			widget=NumberInput(),
			validators=[DataRequired()]))

	s_publishNotifyEditorOnReady = Setting('publish.notify_editor_on_ready',
		BooleanField(
			'Notify the editor when a player marks an article as ready'))

	s_publishNotifyPlayerOnReject = Setting('publish.notify_player_on_reject',
		BooleanField(
			'Notify a player when their article is rejected by the editor'))

	s_publishNotifyPlayerOnAccept = Setting('publish.notify_player_on_accept',
		BooleanField(
			'Notify a player when their article is accepted by the editor'))

	s_publishDeadlines = Setting('publish.deadlines',
		StringField(
			'Turn deadline, as a crontab specification',
			validators=[Optional()]))

	s_publishAsap = Setting('publish.asap',
		BooleanField(
			'Publish the turn immediately when the last article is accepted'))

	s_publishQuorum = Setting('publish.quorum',
		IntegerField(
			'Quorum to publish incomplete turn',
			widget=NumberInput(),
			validators=[Optional()]))

	s_publishBlockOnReady = Setting('publish.block_on_ready',
		BooleanField(
			'Block turn publish if any articles are awaiting editor review'))

	s_articleIndexList = Setting('article.index.list',
		TextAreaField(
			'Index specifications',
			validators=[IndexList]),
		translator=IndexListTranslator())

	s_articleIndexCapacity = Setting('article.index.capacity',
		IntegerField(
			'Index capacity override',
			widget=NumberInput(),
			validators=[Optional()]))

	s_articleCitationAllowSelf = Setting('article.citation.allow_self',
		BooleanField('Allow players to cite themselves'))

	s_articleCitationMinExtant = Setting('article.citation.min_extant',
		IntegerField(
			'Minimum number of extant articles to cite',
			widget=NumberInput(),
			validators=[Optional()]))

	s_articleCitationMaxExtant = Setting('article.citation.max_extant',
		IntegerField(
			'Maximum number of extant articles to cite',
			widget=NumberInput(),
			validators=[Optional()]))

	s_articleCitationMinPhantom = Setting('article.citation.min_phantom',
		IntegerField(
			'Minimum number of phantom articles to cite',
			widget=NumberInput(),
			validators=[Optional()]))

	s_articleCitationMaxPhantom = Setting('article.citation.max_phantom',
		IntegerField(
			'Maximum number of phantom articles to cite',
			widget=NumberInput(),
			validators=[Optional()]))

	s_articleCitationMinTotal = Setting('article.citation.min_total',
		IntegerField(
			'Minimum number of articles to cite in total',
			widget=NumberInput(),
			validators=[Optional()]))

	s_articleCitationMaxTotal = Setting('article.citation.max_total',
		IntegerField(
			'Maximum number of articles to cite in total',
			widget=NumberInput(),
			validators=[Optional()]))

	s_articleCitationMinChars = Setting('article.citation.min_chars',
		IntegerField(
			'Minimum number of characters to cite articles by',
			widget=NumberInput(),
			validators=[Optional()]))

	s_articleCitationMaxChars = Setting('article.citation.max_chars',
		IntegerField(
			'Maximum number of characters to cite articles by',
			widget=NumberInput(),
			validators=[Optional()]))

	s_articleWordLimitSoft = Setting('article.word_limit.soft',
		IntegerField(
			'Soft word limit',
			widget=NumberInput(),
			validators=[Optional()]))

	s_articleWordLimitHard = Setting('article.word_limit.hard',
		IntegerField(
			'Hard word limit',
			widget=NumberInput(),
			validators=[Optional()]))

	s_articleAddendumAllowed = Setting('article.addendum.allowed',
		BooleanField('Allow addendum articles'))

	s_articleAddendumMax = Setting('article.addendum.max',
		IntegerField(
			'Maximum number of addendum articles per character per turn',
			widget=NumberInput(),
			validators=[Optional()]))


class ConfigFormBase(FlaskForm):
	def __init__(self, lexicon):
		super().__init__()
		editor_field = getattr(self, 'editor', None)
		if editor_field:
			model_factory: ModelFactory = current_app.config['model_factory']
			editor_field.choices = list(map(
				lambda s: (s, s),
				map(
					lambda uid: model_factory.user(uid).cfg.username,
					lexicon.cfg.join.joined)))

	def load(self, lexicon):
		for name, setting in Settings.settings():
			field = getattr(self, name[2:], None)
			if field:
				setting.load(lexicon.cfg, field)

	def save(self, lexicon):
		with lexicon.ctx.edit_config() as cfg:
			for name, setting in Settings.settings():
				field = getattr(self, name[2:], None)
				if field:
					setting.save(cfg, field)


for k, v in Settings.settings():
	setattr(ConfigFormBase, k[2:], v.field)
