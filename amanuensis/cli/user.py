import shutil

from amanuensis.cli.helpers import (
	add_argument, no_argument, requires_username,
	config_get, config_set, CONFIG_GET_ROOT_VALUE)

@requires_username
@add_argument("--email", required=True, help="User's email")
@add_argument("--displayname", help="User's publicly displayed name")
def command_create(args):
	"""
	Create a user
	"""
	import json
	# Module imports
	from amanuensis.config import logger, json_ro
	from amanuensis.user import UserModel, valid_username, valid_email, create_user

	# Verify or query parameters
	if not valid_username(args.username):
		logger.error("Invalid username: usernames may only contain alphanumeric characters, dashes, and underscores")
		return -1
	if UserModel.by(name=args.username) is not None:
		logger.error("Invalid username: username is already taken")
		return -1
	if not args.displayname:
		args.displayname = args.username
	if not valid_email(args.email):
		logger.error("Invalid email")
		return -1

	# Create user
	new_user, tmp_pw = create_user(args.username, args.displayname, args.email)
	with json_ro(new_user.config_path) as js:
		print(json.dumps(js, indent=2))
	print("Username: {}\nUser ID:  {}\nPassword: {}".format(args.username, new_user.uid, tmp_pw))

@add_argument("--id", required=True, help="id of user to delete")
def command_delete(args):
	"""
	Delete a user
	"""
	import os
	# Module imports
	from amanuensis.config import logger, prepend

	user_path = prepend('user', args.id)
	if not os.path.isdir(user_path):
		logger.error("No user with that id")
		return -1
	else:
		shutil.rmtree(user_path)
	with json_rw('user', 'index.json') as j:
		if args.id in j:
			del j[uid]

	# TODO

@no_argument
def command_list(args):
	"""List all users"""
	import os
	# Module imports
	from amanuensis.config import prepend, json_ro

	user_dirs = os.listdir(prepend('user'))
	users = []
	for uid in user_dirs:
		if uid == "index.json": continue
		with json_ro('user', uid, 'config.json') as user:
			users.append(user)
	users.sort(key=lambda u: u['username'])
	for user in users:
		print("{0}  {1} ({2})".format(user['uid'], user['displayname'], user['username']))

@requires_username
@add_argument(
	"--get", metavar="PATHSPEC", dest="get",
	nargs="?", const=CONFIG_GET_ROOT_VALUE, help="Get the value of a config key")
@add_argument(
	"--set", metavar=("PATHSPEC", "VALUE"), dest="set",
	nargs=2, help="Set the value of a config key")
def command_config(args):
	"""
	Interact with a user's config
	"""
	import json
	# Module imports
	from amanuensis.config import logger, json_ro, json_rw
	from amanuensis.user import UserModel

	if args.get and args.set:
		logger.error("Specify one of --get and --set")
		return -1

	u = UserModel.by(name=args.username)
	if not u:
		logger.error("User not found")
		return -1

	if args.get:
		with json_ro('user', u.id, 'config.json') as cfg:
			config_get(cfg, args.get)

	if args.set:
		with json_rw('user', u.id, 'config.json') as cfg:
			config_set(u.id, cfg, args.set)

@add_argument("--username", help="The user to change password for")
def command_passwd(args):
	"""
	Set a user's password
	"""
	import getpass
	import os
	# Module imports
	from amanuensis.config import logger
	from amanuensis.user import UserModel

	if not args.username:
		args.username = input("Username: ")
	u = UserModel.by(name=args.username)
	if u is None:
		logger.error("No user with username '{}'".format(args.username))
		return -1
	pw = getpass.getpass("Password: ")
	u.set_password(pw)
