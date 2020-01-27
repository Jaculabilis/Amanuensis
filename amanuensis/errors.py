class AmanuensisError(Exception):
	"""Base class for exceptions in amanuensis"""

class MissingConfigError(AmanuensisError):
	"""A config file is missing that was expected to be present"""

class MalformedConfigError(AmanuensisError):
	"""A config file could not be read and parsed"""

class ReadOnlyError(AmanuensisError):
	"""A config was edited in readonly mode"""

class InternalMisuseError(AmanuensisError):
	"""An internal helper method was called wrongly"""

class IndexMismatchError(AmanuensisError):
	"""An id was obtained from an index, but the object doesn't exist"""
