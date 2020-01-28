# Standard imports
import getpass
import json
import os
import shutil

# Module imports
from amanuensis.cli.helpers import (
	add_argument, no_argument, requires_user,
	config_get, config_set, CONFIG_GET_ROOT_VALUE)


@add_argument("--username", required=True, help="Name of user to create")
@add_argument("--email", help="User's email")
@add_argument("--displayname", help="User's publicly displayed name")
def command_create(args):
	"""
	Create a user
	"""
	# Module imports
	from amanuensis.config import logger, json_ro
	from amanuensis.user import (
		UserModel, valid_username, valid_email, create_user)

	# Verify arguments
	if not valid_username(args.username):
		logger.error("Invalid username: usernames may only contain alphanumer"
			"ic characters, dashes, and underscores")
		return -1
	if UserModel.by(name=args.username) is not None:
		logger.error("Invalid username: username is already taken")
		return -1
	if not args.displayname:
		args.displayname = args.username
	if args.email and not valid_email(args.email):
		logger.error("Invalid email")
		return -1

	# Perform command
	new_user, tmp_pw = create_user(args.username, args.displayname, args.email)

	# Output
	print(tmp_pw)
	return 0


@requires_user
def command_delete(args):
	"""
	Delete a user
	"""
	# Module imports
	from amanuensis.config import logger, prepend, json_rw

	# Perform command
	user_path = prepend('user', args.user.id)
	shutil.rmtree(user_path)
	with json_rw('user', 'index.json') as index:
		del index[args.user.username]

	# TODO resolve user id references in all games

	# Output
	logger.info("Deleted user {0.username} ({0.id})".format(args.user))
	return 0


@no_argument
def command_list(args):
	"""List all users"""
	# Module imports
	from amanuensis.config import prepend, json_ro

	# Perform command
	user_dirs = os.listdir(prepend('user'))
	users = []
	for uid in user_dirs:
		if uid == "index.json":
			continue
		with json_ro('user', uid, 'config.json') as user:
			users.append(user)

	# Output
	users.sort(key=lambda u: u['username'])
	for user in users:
		print("{0}  {1} ({2})".format(
			user['uid'], user['displayname'], user['username']))
	return 0


@requires_user
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
	# Module imports
	from amanuensis.config import logger, json_ro, json_rw
	from amanuensis.user import UserModel

	# Verify arguments
	if args.get and args.set:
		logger.error("Specify one of --get and --set")
		return -1

	# Perform command
	if args.get:
		config_get(args.user.config, args.get)

	if args.set:
		with json_rw(args.user.config_path) as cfg:
			config_set(args.user.id, cfg, args.set)

	# Output
	return 0


@requires_user
@add_argument("--password", help="The password to set. Used for scripting; "
	"not recommended for general use")
def command_passwd(args):
	"""
	Set a user's password
	"""
	# Module imports
	from amanuensis.config import logger
	from amanuensis.user import UserModel

	# Verify arguments
	pw = args.password or getpass.getpass("Password: ")

	# Perform commands
	args.user.set_password(pw)

	# Output
	return 0
