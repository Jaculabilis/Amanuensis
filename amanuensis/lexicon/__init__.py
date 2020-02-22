import os
import time

from amanuensis.errors import (
	ArgumentError, IndexMismatchError, MissingConfigError)
from amanuensis.config import prepend, json_ro, json_rw, root

class LexiconModel():
	@staticmethod
	def by(lid=None, name=None):
		"""
		Gets the LexiconModel with the given lid or username

		If the lid or name simply does not match an existing lexicon, returns
		None. If the lid matches the index but there is something wrong with
		the lexicon's config, raises an error.
		"""
		if lid and name:
			raise ArgumentError("lid and name both specified to Lexicon"
				"Model.by()")
		if not lid and not name:
			raise ArgumentError("One of lid or name must be not None")
		if not lid:
			with json_ro('lexicon', 'index.json') as index:
				lid = index.get(name)
		if not lid:
			return None
		if not os.path.isdir(prepend('lexicon', lid)):
			raise IndexMismatchError("lexicon={} lid={}".format(name, lid))
		if not os.path.isfile(prepend('lexicon', lid, 'config.json')):
			raise MissingConfigError("lid={}".format(lid))
		return LexiconModel(lid)

	def __init__(self, lid):
		if not os.path.isdir(prepend('lexicon', lid)):
			raise ValueError("No lexicon with lid {}".format(lid))
		if not os.path.isfile(prepend('lexicon', lid, 'config.json')):
			raise FileNotFoundError("Lexicon {} missing config.json".format(lid))
		self.id = str(lid)
		self.config_path = prepend('lexicon', lid, 'config.json')
		with json_ro(self.config_path) as j:
			self.config = j
		self.ctx = root.lexicon[self.id]

	def __getattr__(self, key):
		if key not in self.config:
			raise AttributeError(key)
		if key == 'title':
			return self.config.get('title') or f'Lexicon {self.config.name}'
		return self.config.get(key)

	def __str__(self):
		return '<Lexicon {0.name}>'.format(self)

	def __repr__(self):
		return '<LexiconModel lid={0.id} name={0.name}>'.format(self)

	def edit(self):
		return json_rw(self.config_path)

	def add_log(self, message):
		now = int(time.time())
		with self.edit() as j:
			j['log'].append([now, message])

	def status(self):
		if self.turn.current is None:
			return "unstarted"
		if self.turn.current > self.turn.max:
			return "completed"
		return "ongoing"

	def can_add_character(self, uid):
		return (
			# Players can't add more characters than chars_per_player
			(len(self.get_characters_for_player(uid))
				< self.join.chars_per_player)
			# Characters can only be added before the game starts
			and not self.turn.current)

	def get_characters_for_player(self, uid=None):
		return [
			char for char in self.character.values()
			if uid is None or char.player == uid]

	def get_drafts_for_player(self, uid):
		chars = self.get_characters_for_player(uid=uid)
		drafts_path = prepend('lexicon', self.id, 'draft')
		drafts = []
		for filename in os.listdir(drafts_path):
			for char in chars:
				if filename.startswith(str(char.cid)):
					drafts.append(filename)
		for i in range(len(drafts)):
			with json_ro(drafts_path, drafts[i]) as a:
				drafts[i] = a
		return drafts
