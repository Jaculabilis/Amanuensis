from amanuensis.config import is_guid, RootConfigDirectoryContext
from amanuensis.errors import ArgumentError
from amanuensis.models.user import UserModel
from amanuensis.models.lexicon import LexiconModel


class ModelFactory():
	def __init__(self, root: RootConfigDirectoryContext):
		self.root: RootConfigDirectoryContext = root

	def user(self, identifier: str) -> UserModel:
		"""Get the user model for the given id or username"""
		# Ensure we have something to work with
		if identifier is None:
			raise ArgumentError('identifer must not be None')
		# Ensure we have a user guid
		if not is_guid(identifier):
			with self.root.user.index() as index:
				uid = index.get(identifier, None)
			if uid is None:
				raise KeyError(f'Unknown username: {identifier})')
			if not is_guid(uid):
				raise ValueError(f'Invalid index entry: {uid}')
		else:
			uid = identifier
		user = UserModel(self.root, uid)
		return user

	def lexicon(self, identifier: str) -> LexiconModel:
		"""Get the lexicon model for the given id or name"""
		# Ensure we have something to work with
		if identifier is None:
			raise ArgumentError('identifier must not be None')
		# Ensure we have a lexicon guid
		if not is_guid(identifier):
			with self.root.lexicon.index() as index:
				lid = index.get(identifier, None)
			if lid is None:
				raise KeyError(f'Unknown lexicon: {identifier}')
			if not is_guid(lid):
				raise ValueError(f'Invalid index entry: {lid}')
		else:
			lid = identifier
		lexicon = LexiconModel(self.root, lid)
		return lexicon
