"""
Dictionary classes used to represent JSON config files in memory.
"""
from collections import OrderedDict

from amanuensis.errors import ReadOnlyError


class AttrOrderedDict(OrderedDict):
	"""
	An OrderedDict with attribute access to known keys and explicit
	creation of new keys.
	"""
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
	"""
	An OrderedDict that cannot be modified with attribute access to
	known keys.
	"""
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
