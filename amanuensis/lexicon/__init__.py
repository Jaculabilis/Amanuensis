import os
import time

from amanuensis.errors import InternalMisuseError, IndexMismatchError, MissingConfigError
from amanuensis.config import prepend, json_ro, json_rw

class LexiconModel():
	def by(lid=None, name=None):
		"""
		Gets the LexiconModel with the given lid or username

		If the lid or name simply does not match an existing lexicon, returns
		None. If the lid matches the index but there is something wrong with
		the lexicon's config, raises an error.
		"""
		if lid and name:
			raise InternalMisuseError("lid and name both specified to LexiconModel.by()")
		if not lid and not name:
			raise ValueError("One of lid or name must be not None")
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

	def __getattr__(self, key):
		if key not in self.config:
			raise AttributeError(key)
		return self.config.get(key)

	def log(self, message):
		now = int(time.time())
		with json_rw(self.config_path) as j:
			j['log'].append([now, message])

	def status(self):
		if self.turn.current is None:
			return "unstarted"
		elif self.turn.current > self.turn.max:
			return "completed"
		else:
			return "ongoing"