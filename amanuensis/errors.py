class AmanuensisError(Exception):
	"""Base class for exceptions in amanuensis"""

class MissingConfigError(AmanuensisError):
	"""A config file is missing that was expected to be present"""
	def __init__(self, path):
		super().__init__("A config file or directory was expected to "
			f"exist, but could not be found: {path}")

class ConfigAlreadyExistsError(AmanuensisError):
	"""Attempted to create a config, but it already exists"""
	def __init__(self, path):
		super().__init__("Attempted to create a config, but it already "
			f"exists: {path}")

class MalformedConfigError(AmanuensisError):
	"""A config file could not be read and parsed"""

class ReadOnlyError(AmanuensisError):
	"""A config was edited in readonly mode"""

class ArgumentError(AmanuensisError):
	"""An internal call was made with invalid arguments"""

class IndexMismatchError(AmanuensisError):
	"""An id was obtained from an index, but the object doesn't exist"""
