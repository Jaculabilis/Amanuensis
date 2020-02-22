import os
import re

from amanuensis.config.loader import json_ro, json_rw
from amanuensis.errors import MissingConfigError, ConfigAlreadyExistsError


def is_guid(s):
	return re.match(r'[0-9a-z]{32}', s.lower())


class ConfigDirectoryContext():
	"""
	Base class for CRUD operations on config files in a config
	directory.
	"""
	def __init__(self, path):
		self.path = path
		if not os.path.isdir(self.path):
			raise MissingConfigError(path)

	def new(self, filename):
		"""
		Creates a JSON file that doesn't already exist.
		"""
		if not filename.endswith('.json'):
			filename = f'{filename}.json'
		fpath = os.path.join(self.path, filename)
		if os.path.isfile(fpath):
			raise ConfigAlreadyExistsError(fpath)
		return json_rw(fpath, new=True)

	def read(self, filename):
		"""
		Loads a JSON file in read-only mode.
		"""
		if not filename.endswith('.json'):
			filename = f'{filename}.json'
		fpath = os.path.join(self.path, filename)
		if not os.path.isfile(fpath):
			raise MissingConfigError(fpath)
		return json_ro(fpath)

	def edit(self, filename):
		"""
		Loads a JSON file in write mode.
		"""
		if not filename.endswith('.json'):
			filename = f'{filename}.json'
		fpath = os.path.join(self.path, filename)
		if not os.path.isfile(fpath):
			raise MissingConfigError(fpath)
		return json_rw(fpath, new=False)

	def delete(self, filename):
		"""Deletes a file."""
		if not filename.endswith('.json'):
			filename = f'{filename}.json'
		fpath = os.path.join(self.path, filename)
		if not os.path.isfile(fpath):
			raise MissingConfigError(fpath)
		os.delete(fpath)


class IndexDirectoryContext(ConfigDirectoryContext):
	"""
	A lookup layer for getting config directory contexts for lexicon
	or user directories.
	"""
	def __init__(self, path, cdc_type):
		super().__init__(path)
		self.cdc_type = cdc_type

	def __getitem__(self, key):
		"""
		Returns a context to the given item. key is treated as the
		item's id if it's a guid string, otherwise it's treated as
		the item's indexed name and run through the index first.
		"""
		if not is_guid(key):
			with self.index() as index:
				iid = index.get(key)
				if not iid:
					raise MissingConfigError(key)
				key = iid
		return self.cdc_type(os.path.join(self.path, key))

	def index(self, edit=False):
		if edit:
			return self.edit('index')
		else:
			return self.read('index')


class RootConfigDirectoryContext(ConfigDirectoryContext):
	"""
	Context for the config directory with links to the lexicon and
	user contexts.
	"""
	def __init__(self, path):
		super().__init__(path)
		self.lexicon = IndexDirectoryContext(
			os.path.join(self.path, 'lexicon'),
			LexiconConfigDirectoryContext)
		self.user = IndexDirectoryContext(
			os.path.join(self.path, 'user'),
			UserConfigDirectoryContext)


class LexiconConfigDirectoryContext(ConfigDirectoryContext):
	"""
	A config context for a lexicon's config directory.
	"""
	def __init__(self, path):
		super().__init__(path)
		self.draft = ConfigDirectoryContext(os.path.join(self.path, 'draft'))
		self.src = ConfigDirectoryContext(os.path.join(self.path, 'src'))

	def config(edit=False):
		if edit:
			return self.edit('config')
		else:
			return self.read('config')


class UserConfigDirectoryContext(ConfigDirectoryContext):
	"""
	A config context for a user's config directory.
	"""
	def config(edit=False):
		if edit:
			return self.edit('config')
		else:
			return self.read('config')
