import os
import re
import time
import uuid

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

import config

class User(UserMixin):
	def __init__(self, uid):
		if not os.path.isdir(config.prepend('user', uid)):
			raise ValueError("No user with uid {}".format(uid))
		self.uid = str(uid)
		self.config_path = os.path.join('user', uid, 'config.json')
		with config.json_ro(self.config_path) as j:
			self.config = j

	def __getattr__(self, key):
		if key not in self.config:
			raise AttributeError(key)
		return self.config.get(key)

	def get_id(self):
		return self.uid

	def set_password(self, pw):
		h = generate_password_hash(pw)
		with config.json_rw(self.config_path) as j:
			j['password'] = h

	def check_password(self, pw):
		with config.json_ro(self.config_path) as j:
			return check_password_hash(j['password'], pw)

def valid_username(username):
	return re.match(r"^[A-Za-z0-9-_]{3,}$", username) is not None

def valid_email(email):
	"""Vaguely RFC2822 email verifier"""
	atom = r"[0-9A-Za-z!#$%&'*+-/=?^_`{|}~]{1,}"
	dotatom = atom + r"(\." + atom + r")*"
	addrspec = "^" + dotatom + "@" + dotatom + "$"
	return re.match(addrspec, email)

def create_user(username, displayname, email):
	if not valid_username(username):
		raise ValueError("Invalid username: '{}'".format(username))
	if not valid_email(email):
		raise ValueError("Invalid email: '{}'".format(email))
	uid = uuid.uuid4().hex
	now = int(time.time())
	temp_pw = os.urandom(32).hex()
	user_json = {
		'uid': uid,
		'username': username,
		'displayname': displayname,
		'email': email,
		'password': None,
		'created': now,
		'newPasswordRequired': True,
		'admin': False,
	}
	config.new_user(user_json)
	u = User(uid)
	u.set_password(temp_pw)
	return u, temp_pw

def uid_from_username(username):
	"""Gets the internal uid of a user given a username"""
	if username is None:
		raise ValueError("username must not be None")
	if not username:
		raise ValueError("username must not be empty")
	with config.json_ro('user', 'index.json') as index:
		uid = index.get(username)
	if uid is None:
		config.logger.debug("uid_from_username('{}') returned None".format(username))
	return uid

def user_from_uid(uid):
	if not os.path.isdir(config.prepend('user', uid)):
		config.logger.debug("No user with uid '{}'".format(uid))
		return None
	return User(uid)
