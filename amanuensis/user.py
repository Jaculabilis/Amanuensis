import os
import re
import time
import uuid

from werkzeug.security import generate_password_hash, check_password_hash

import config

class User():
	def __init__(self, uid):
		if not os.path.isdir(config.prepend('user', uid)):
			raise ValueError("No user with uid {}".format(uid))
		self.uid = uid
		self.config = os.path.join('user', uid, 'config.json')

	def set_password(self, pw):
		h = generate_password_hash(pw)
		with config.json_rw(self.config) as j:
			j['password'] = h

	def check_password(self, pw):
		with config.json_ro(self.config) as j:
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
	uid = uuid.uuid4().hex
	now = int(time.time())
	user_json = {
		'uid': uid,
		'username': username,
		'displayname': displayname,
		'email': email,
		'password': None,
		'created': now,
	}
	config.new_user(user_json)
	return User(uid)

def get_user_by_username(username):
	with config.json_ro('user', 'index.json') as index:
		return index.get(username)
