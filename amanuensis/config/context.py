"""
`with` context managers for mediating config file access.
"""
# Standard library imports
import fcntl
import json

# Application imports
from .dict import AttrOrderedDict, ReadOnlyOrderedDict


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

	def __enter__(self) -> ReadOnlyOrderedDict:
		self.config = json.load(self.fd, object_pairs_hook=ReadOnlyOrderedDict)
		return self.config


class json_rw(open_ex):
	"""
	A context manager that opens a file with an exclusive lock. The
	file mode defaults to r+, which requires that the file exist. The
	file mode can be set to w+ to create a new file by setting the new
	kwarg in the ctor. The contents of the file are read as JSON and
	returned in an AttrOrderedDict. Any changes to the context dict
	will be written out to the file when the context manager exits,
	unless an exception is raised before exiting.
	"""
	def __init__(self, path, new=False):
		mode = 'w+' if new else 'r+'
		super().__init__(path, mode)
		self.config = None
		self.new = new

	def __enter__(self) -> AttrOrderedDict:
		if not self.new:
			self.config = json.load(self.fd, object_pairs_hook=AttrOrderedDict)
		else:
			self.config = AttrOrderedDict()
		return self.config

	def __exit__(self, exc_type, exc_value, traceback):
		# Only write the new value out if there wasn't an exception
		if not exc_type:
			self.fd.seek(0)
			json.dump(self.config, self.fd, allow_nan=False, indent='\t')
			self.fd.truncate()
		super().__exit__(exc_type, exc_value, traceback)
