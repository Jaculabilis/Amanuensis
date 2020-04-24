"""
Config directory abstractions that encapsulate path munging and context
manager usage.
"""
import os
import re
from typing import Iterable

from amanuensis.config.context import json_ro, json_rw
from amanuensis.errors import MissingConfigError, ConfigAlreadyExistsError


def is_guid(s: str) -> bool:
	return bool(re.match(r'[0-9a-z]{32}', s.lower()))


class ConfigDirectoryContext():
	"""
	Base class for CRUD operations on config files in a config
	directory.
	"""
	def __init__(self, path: str):
		self.path: str = path
		if not os.path.isdir(self.path):
			raise MissingConfigError(path)

	def new(self, filename) -> json_rw:
		"""
		Creates a JSON file that doesn't already exist.
		"""
		if not filename.endswith('.json'):
			filename = f'{filename}.json'
		fpath: str = os.path.join(self.path, filename)
		if os.path.isfile(fpath):
			raise ConfigAlreadyExistsError(fpath)
		return json_rw(fpath, new=True)

	def read(self, filename) -> json_ro:
		"""
		Loads a JSON file in read-only mode.
		"""
		if not filename.endswith('.json'):
			filename = f'{filename}.json'
		fpath: str = os.path.join(self.path, filename)
		if not os.path.isfile(fpath):
			raise MissingConfigError(fpath)
		return json_ro(fpath)

	def edit(self, filename, create=False) -> json_rw:
		"""
		Loads a JSON file in write mode.
		"""
		if not filename.endswith('.json'):
			filename = f'{filename}.json'
		fpath: str = os.path.join(self.path, filename)
		if not create and not os.path.isfile(fpath):
			raise MissingConfigError(fpath)
		return json_rw(fpath, new=create)

	def delete(self, filename) -> None:
		"""Deletes a file."""
		if not filename.endswith('.json'):
			filename = f'{filename}.json'
		fpath: str = os.path.join(self.path, filename)
		if not os.path.isfile(fpath):
			raise MissingConfigError(fpath)
		os.remove(fpath)

	def ls(self) -> Iterable[str]:
		"""Lists all files in this directory."""
		filenames: Iterable[str] = os.listdir(self.path)
		return filenames


class ConfigFileConfigDirectoryContext(ConfigDirectoryContext):
	"""
	Config directory with a `config.json`.
	"""
	def __init__(self, path: str):
		super().__init__(path)
		config_path = os.path.join(self.path, 'config.json')
		if not os.path.isfile(config_path):
			raise MissingConfigError(config_path)

	def edit_config(self) -> json_rw:
		"""rw context manager for this object's config file."""
		return self.edit('config')

	def read_config(self) -> json_ro:
		"""ro context manager for this object's config file."""
		return self.read('config')


class IndexDirectoryContext(ConfigDirectoryContext):
	"""
	A lookup layer for getting config directory contexts for lexicon
	or user directories.
	"""
	def __init__(self, path: str, cdc_type: type):
		super().__init__(path)
		index_path = os.path.join(self.path, 'index.json')
		if not os.path.isfile(index_path):
			raise MissingConfigError(index_path)
		self.cdc_type = cdc_type

	def __getitem__(self, key: str) -> ConfigFileConfigDirectoryContext:
		"""
		Returns a context to the given item. key is treated as the
		item's id if it's a guid string, otherwise it's treated as
		the item's indexed name and run through the index first.
		"""
		if not is_guid(key):
			with self.read_index() as index:
				iid = index.get(key)
				if not iid:
					raise MissingConfigError(key)
				key = iid
		return self.cdc_type(os.path.join(self.path, key))

	def edit_index(self) -> json_rw:
		return self.edit('index')

	def read_index(self) -> json_ro:
		return self.read('index')


class RootConfigDirectoryContext(ConfigFileConfigDirectoryContext):
	"""
	Context for the config directory with links to the lexicon and
	user contexts.
	"""
	def __init__(self, path):
		super().__init__(path)
		self.lexicon: IndexDirectoryContext = IndexDirectoryContext(
			os.path.join(self.path, 'lexicon'),
			LexiconConfigDirectoryContext)
		self.user: IndexDirectoryContext = IndexDirectoryContext(
			os.path.join(self.path, 'user'),
			UserConfigDirectoryContext)


class LexiconConfigDirectoryContext(ConfigFileConfigDirectoryContext):
	"""
	A config context for a lexicon's config directory.
	"""
	def __init__(self, path):
		super().__init__(path)
		self.draft: ConfigDirectoryContext = ConfigDirectoryContext(
			os.path.join(self.path, 'draft'))
		self.src: ConfigDirectoryContext = ConfigDirectoryContext(
			os.path.join(self.path, 'src'))
		self.article: ConfigDirectoryContext = ConfigDirectoryContext(
			os.path.join(self.path, 'article'))


class UserConfigDirectoryContext(ConfigFileConfigDirectoryContext):
	"""
	A config context for a user's config directory.
	"""
