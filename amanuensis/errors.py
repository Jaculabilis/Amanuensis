class AmanuensisError(Exception):
	"""Base class for exceptions in amanuensis"""
	pass

class MissingConfigError(AmanuensisError):
	pass

class MalformedConfigError(AmanuensisError):
	pass

class ReadOnlyError(AmanuensisError):
	pass
