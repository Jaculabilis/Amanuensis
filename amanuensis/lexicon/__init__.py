import os
import time

import config

class LexiconModel():
	"""
	"""
	def __init__(self, lid):
		if not os.path.isdir(config.prepend('lexicon', lid)):
			raise ValueError("No lexicon with lid {}".format(lid))
		if not os.path.isfile(config.prepend('lexicon', lid, 'config.json')):
			raise FileNotFoundError("Lexicon {} missing config.json".format(lid))
		self.id = str(lid)
		self.config_path = config.prepend('lexicon', lid, 'config.json')
		with config.json_ro(self.config_path) as j:
			self.config = j

	def __getattr__(self, key):
		if key not in self.config:
			raise AttributeError(key)
		return self.config.get(key)

	def log(self, message):
		now = int(time.time())
		with config.json_rw(self.config_path) as j:
			j['log'].append([now, message])