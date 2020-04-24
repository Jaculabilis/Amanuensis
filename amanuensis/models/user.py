from typing import cast

from werkzeug.security import generate_password_hash, check_password_hash

from amanuensis.config import (
	RootConfigDirectoryContext,
	UserConfigDirectoryContext,
	ReadOnlyOrderedDict)
from amanuensis.config.context import json_rw


class UserModelBase():
	"""Common base class for auth and anon user models"""

	# Properties

	@property
	def uid(self) -> str:
		"""User guid"""
		return getattr(self, '_uid', None)

	@property
	def ctx(self) -> UserConfigDirectoryContext:
		"""User config directory context"""
		return getattr(self, '_ctx', None)

	@property
	def cfg(self) -> ReadOnlyOrderedDict:
		"""Cached user config"""
		return getattr(self, '_cfg', None)

	# Flask-Login interfaces

	@property
	def is_authenticated(self) -> bool:
		return self.uid is not None

	@property
	def is_active(self) -> bool:
		return self.uid is not None

	@property
	def is_anonymous(self) -> bool:
		return self.uid is None

	def get_id(self) -> str:
		return self.uid


class UserModel(UserModelBase):
	"""Represents a user in the Amanuensis config store"""
	def __init__(self, root: RootConfigDirectoryContext, uid: str):
		self._uid: str = uid
		# Creating the config context implicitly checks for existence
		self._ctx: UserConfigDirectoryContext = root.user[uid]
		with self._ctx.config(edit=False) as config:
			self._cfg: ReadOnlyOrderedDict = cast(ReadOnlyOrderedDict, config)

	def __str__(self) -> str:
		return f'<{self.cfg.username}>'

	def __repr__(self) -> str:
		return f'<UserModel({self.uid})>'

	# Utility methods

	def edit(self) -> json_rw:
		return cast(json_rw, self.ctx.config(edit=True))

	def set_password(self, password: str) -> None:
		pw_hash = generate_password_hash(password)
		with self.edit() as cfg:
			cfg['password'] = pw_hash

	def check_password(self, password) -> bool:
		with self.ctx.config() as cfg:
			return check_password_hash(cfg.password, password)


class AnonymousUserModel(UserModelBase):
	"""Represents an anonymous user"""
	def __str__(self) -> str:
		return '<Anonymous>'

	def __repr__(self) -> str:
		return '<AnonymousUserModel>'
