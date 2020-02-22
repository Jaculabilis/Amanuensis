# Standard library imports
from collections import OrderedDict
import fcntl
import json

# Module imports
from amanuensis.errors import ReadOnlyError


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
	"""A context manager that opens a file with the specified file lock"""
	def __init__(self, path, mode, lock_type):
		self.fd = open(path, mode, encoding='utf8')
		fcntl.lockf(self.fd, lock_type)

	def __enter__(self):
		return self.fd

	def __exit__(self, exc_type, exc_value, traceback):
		fcntl.lockf(self.fd, fcntl.LOCK_UN)
		self.fd.close()


class open_sh(open_lock):
	"""A context manager that opens a file with a shared lock"""
	def __init__(self, path, mode):
		super().__init__(path, mode, fcntl.LOCK_SH)


class open_ex(open_lock):
	"""A context manager that opens a file with an exclusive lock"""
	def __init__(self, path, mode):
		super().__init__(path, mode, fcntl.LOCK_EX)


class json_ro(open_sh):
	"""
	A context manager that opens a file in a shared, read-only mode.
	The contents of the file are read as JSON and returned as a read-
	only OrderedDict.
	"""
	def __init__(self, path):
		super().__init__(path, 'r')
		self.config = None

	def __enter__(self):
		self.config = json.load(self.fd, object_pairs_hook=ReadOnlyOrderedDict)
		return self.config


class json_rw(open_ex):
	"""
	A context manager that opens a file with an exclusive lock. The
	file mode defaults to r+, which requires that the file exist. The
	file mode can be set to w+ to create a new file by setting the new
	kwarg in the ctor. The contents of the file are read as JSON and
	returned in an AttrOrderedDict. Any changes to the context dict
	will be written out to the file when the context manager exits.
	"""
	def __init__(self, path, new=False):
		mode = 'w+' if new else 'r+'
		super().__init__(path, mode)
		self.config = None
		self.new = new

	def __enter__(self):
		if not self.new:
			self.config = json.load(self.fd, object_pairs_hook=AttrOrderedDict)
		else:
			self.config = AttrOrderedDict()
		return self.config

	def __exit__(self, exc_type, exc_value, traceback):
		# Only write the enw value out if there wasn't an exception
		if not exc_type:
			self.fd.seek(0)
			json.dump(self.config, self.fd, allow_nan=False, indent='\t')
			self.fd.truncate()
		super().__exit__(exc_type, exc_value, traceback)
