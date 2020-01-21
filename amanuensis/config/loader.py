# Standard library imports
from collections import OrderedDict
import fcntl
import json
import os

# Module imports
from errors import ReadOnlyError


class AttrOrderedDict(OrderedDict):
	"""An ordered dictionary with access via __getattr__"""
	def __getattr__(self, key):
		if key not in self:
			raise AttributeError(key)
		return self[key]

	def __setattr__(self, key, value):
		if key not in self:
			raise AttributeError(key)
		self[key] = value

	def new(self, key, value):
		"""Setter for adding new keys"""
		if key in self:
			raise KeyError("Key already exists: '{}'".format(key))
		self[key] = value


class ReadOnlyOrderedDict(OrderedDict):
	"""An ordered dictionary that cannot be modified"""
	def __readonly__(self, *args, **kwargs):
		raise ReadOnlyError("Cannot modify a ReadOnlyOrderedDict")

	def __init__(self, *args, **kwargs):
		super(ReadOnlyOrderedDict, self).__init__(*args, **kwargs)
		self.__setitem__ = self.__readonly__
		self.__delitem__ = self.__readonly__
		self.pop = self.__readonly__
		self.popitem = self.__readonly__
		self.clear = self.__readonly__
		self.update = self.__readonly__
		self.setdefault = self.__readonly__

	def __getattr__(self, key):
		if key not in self:
			raise AttributeError(key)
		return self[key]

class open_lock():
	def __init__(self, path, mode, lock_type):
		self.fd = open(path, mode, encoding='utf8')
		fcntl.lockf(self.fd, lock_type)

	def __enter__(self):
		return self.fd

	def __exit__(self, exc_type, exc_value, traceback):
		fcntl.lockf(self.fd, fcntl.LOCK_UN)
		self.fd.close()

class open_sh(open_lock):
	def __init__(self, path, mode):
		super().__init__(path, mode, fcntl.LOCK_SH)

class open_ex(open_lock):
	def __init__(self, path, mode):
		super().__init__(path, mode, fcntl.LOCK_EX)

class json_ro(open_sh):
	def __init__(self, path):
		super().__init__(path, 'r')
		self.config = None

	def __enter__(self):
		self.config = json.load(self.fd, object_pairs_hook=ReadOnlyOrderedDict)
		return self.config

class json_rw(open_ex):
	def __init__(self, path):
		super().__init__(path, 'r+')
		self.config = None

	def __enter__(self):
		self.config = json.load(self.fd, object_pairs_hook=AttrOrderedDict)
		return self.config

	def __exit__(self, exc_type, exc_value, traceback):
		self.fd.seek(0)
		json.dump(self.config, self.fd, allow_nan=False, indent='\t')
		self.fd.truncate()
		super().__exit__(exc_type, exc_value, traceback)

