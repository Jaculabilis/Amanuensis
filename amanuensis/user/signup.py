"""
Submodule encapsulating functionality pertaining to creating users in
an Amanuensis instance.
"""
import os
import re
import time
from typing import Tuple
import uuid

from amanuensis.config import RootConfigDirectoryContext
from amanuensis.errors import ArgumentError
from amanuensis.models import ModelFactory, UserModel
from amanuensis.resources import get_stream


def valid_username(username: str) -> bool:
	"""
	A valid username is at least three characters long and composed solely of
	alpahnumerics, dashes, and underscores. Additionally, usernames may not
	be 32 hex digits, since that may be confused for an internal id.
	"""
	length_and_characters = re.match(r'^[A-Za-z0-9-_]{3,}$', username)
	is_a_guid = re.match(r'^[A-Za-z0-9]{32}$', username)
	return bool(length_and_characters and not is_a_guid)


def valid_email(email: str) -> bool:
	"""Vaguely RFC2822 email verifier"""
	atom = r"[0-9A-Za-z!#$%&'*+-/=?^_`{|}~]{1,}"
	dotatom = atom + r"(\." + atom + r")*"
	addrspec = '^' + dotatom + '@' + dotatom + '$'
	return bool(re.match(addrspec, email))


def create_user(
	root: RootConfigDirectoryContext,
	model_factory: ModelFactory,
	username: str,
	displayname: str,
	email: str) -> Tuple[UserModel, str]:
	"""
	Creates a new user
	"""
	# Validate arguments
	if not valid_username(username):
		raise ArgumentError('Invalid username: "{}"'.format(username))
	if email and not valid_email(email):
		raise ArgumentError('Invalid email: "{}"'.format(email))

	# Create the user directory and config file
	uid: str = uuid.uuid4().hex
	user_dir: str = os.path.join(root.user.path, uid)
	os.mkdir(user_dir)
	with get_stream('user.json') as s:
		path: str = os.path.join(user_dir, 'config.json')
		with open(path, 'wb') as f:
			f.write(s.read())

	# Create the user index entry
	with root.user.edit_index() as index:
		index[username] = uid

	# Fill out the new user
	with root.user[uid].edit_config() as cfg:
		cfg.uid = uid
		cfg.username = username
		cfg.displayname = displayname
		cfg.email = email
		cfg.created = int(time.time())

	# Load the user model and set a temporary password
	temporary_password = os.urandom(32).hex()
	user = model_factory.user(uid)
	user.set_password(temporary_password)

	return user, temporary_password
