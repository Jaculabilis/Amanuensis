import os
import re
import time
import uuid

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from errors import InternalMisuseError, MissingConfigError, IndexMismatchError
import config
import resources
import lexicon.manage

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
			raise InternalMisuseError("uid and name both specified to UserModel.by()")
		if not uid and not name:
			raise ValueError("One of uid or name must be not None")
		if not uid:
			with config.json_ro('user', 'index.json') as index:
				uid = index.get(name)
		if not uid:
			return None
		if not os.path.isdir(config.prepend('user', uid)):
			raise IndexMismatchError("username={} uid={}".format(name, uid))
		if not os.path.isfile(config.prepend('user', uid, 'config.json')):
			raise MissingConfigError("uid={}".format(uid))
		return UserModel(uid)

	def __init__(self, uid):
		"""User model initializer, assume all checks were done by by()"""
		self.id = str(uid) # Flask-Login checks for this
		self.config_path = config.prepend('user', uid, 'config.json')
		with config.json_ro(self.config_path) as j:
			self.config = j

	def __getattr__(self, key):
		if key not in self.config:
			raise AttributeError(key)
		return self.config.get(key)

	def set_password(self, pw):
		h = generate_password_hash(pw)
		with config.json_rw(self.config_path) as j:
			j['password'] = h

	def check_password(self, pw):
		with config.json_ro(self.config_path) as j:
			return check_password_hash(j['password'], pw)

	def lexicons_in(self):
		return [
			lex
			for lex in lexicon.manage.get_all_lexicons()
			if self.id in lex.join.joined
		]


def valid_username(username):
	return re.match(r"^[A-Za-z0-9-_]{3,}$", username) is not None

def valid_email(email):
	"""Vaguely RFC2822 email verifier"""
	atom = r"[0-9A-Za-z!#$%&'*+-/=?^_`{|}~]{1,}"
	dotatom = atom + r"(\." + atom + r")*"
	addrspec = "^" + dotatom + "@" + dotatom + "$"
	return re.match(addrspec, email)

def create_user(username, displayname, email):
	"""
	Creates a new user
	"""
	# Validate arguments
	if not valid_username(username):
		raise ValueError("Invalid username: '{}'".format(username))
	if not valid_email(email):
		raise ValueError("Invalid email: '{}'".format(email))

	# Create the user directory and initialize it with a blank user
	uid = uuid.uuid4().hex
	user_dir = config.prepend("user", uid)
	os.mkdir(user_dir)
	with resources.get_stream("user.json") as s:
		with open(config.prepend(user_dir, 'config.json'), 'wb') as f:
			f.write(s.read())

	# Fill out the new user
	with config.json_rw(user_dir, 'config.json') as cfg:
		cfg['uid'] = uid
		cfg['username'] = username
		cfg['displayname'] = displayname
		cfg['email'] = email
		cfg['created'] = int(time.time())

	# Update the index with the new user
	with config.json_rw('user', 'index.json') as index:
		index[username] = uid

	# Set a temporary password
	temp_pw = os.urandom(32).hex()
	u = UserModel.by(uid=uid)
	u.set_password(temp_pw)

	return u, temp_pw
