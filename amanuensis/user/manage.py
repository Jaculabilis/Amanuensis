"""
General functions for managing users
"""
from typing import Iterable

from amanuensis.config import RootConfigDirectoryContext
from amanuensis.models import ModelFactory, UserModel


def load_all_users(
	root: RootConfigDirectoryContext) -> Iterable[UserModel]:
	"""
	Iterably loads every lexicon in the config store
	"""
	model_factory: ModelFactory = ModelFactory(root)
	with root.user.read_index() as index:
		for uid in index.values():
			user: UserModel = model_factory.user(uid)
			yield user
