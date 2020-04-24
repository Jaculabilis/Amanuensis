import os
import re
import time
import uuid

from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from amanuensis.errors import (
	ArgumentError, MissingConfigError, IndexMismatchError)
from amanuensis.config import prepend, json_rw, root
from amanuensis.resources import get_stream


class UserModel(UserMixin):
	@staticmethod
	def by(uid=None, name=None):
		"""
		Gets the UserModel with the given uid or username

		If the uid or name simply does not match an existing user, returns
		None. If the uid matches the index but there is something wrong with
		the user's config, raises an error.
		"""
		if uid and name:
			raise ArgumentError("uid and name both specified to UserModel.by()")
		if not uid and not name:
			raise ArgumentError("One of uid or name must be not None")
		if not uid:
			with root.user.index() as index:
				uid = index.get(name)
		if not uid:
			return None
		if not os.path.isdir(prepend('user', uid)):
			raise IndexMismatchError("username={} uid={}".format(name, uid))
		if not os.path.isfile(prepend('user', uid, 'config.json')):
			raise MissingConfigError("uid={}".format(uid))
		return UserModel(uid)

	def __init__(self, uid):
		"""User model initializer, assume all checks were done by by()"""
		self.id = str(uid) # Flask-Login checks for this
		self.config_path = prepend('user', uid, 'config.json')
		self.ctx = root.user[self.id]
		with self.ctx.config() as j:
			self.config = j

	def __getattr__(self, key):
		if key not in self.config:
			raise AttributeError(key)
		return self.config.get(key)

	def __str__(self):
		return '<{0.username}>'.format(self)

	def __repr__(self):
		return '<UserModel uid={0.id} username={0.username}>'.format(self)

	def set_password(self, pw):
		h = generate_password_hash(pw)
		with self.ctx.config(edit=True) as j:
			j['password'] = h

	def check_password(self, pw):
		with self.ctx.config() as cfg:
			return check_password_hash(cfg.password, pw)

	def in_lexicon(self, lexicon):
		return self.id in lexicon.join.joined


class AnonymousUserModel(AnonymousUserMixin):
	is_admin = False

	def in_lexicon(self, lexicon):
		return False

