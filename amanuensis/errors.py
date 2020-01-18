class AmanuensisError(Exception):
	"""Base class for exceptions in amanuensis"""
	pass

class MissingConfigError(AmanuensisError):
	"""A config file is missing that was expected to be present"""
	pass

class MalformedConfigError(AmanuensisError):
	"""A config file could not be read and parsed"""
	pass

class ReadOnlyError(AmanuensisError):
	"""A config was edited in readonly mode"""
	pass

class InternalMisuseError(AmanuensisError):
	"""An internal helper method was called wrongly"""
	pass

class IndexMismatchError(AmanuensisError):
	"""An id was obtained from an index, but the object doesn't exist"""
	pass