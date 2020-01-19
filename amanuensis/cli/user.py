from cli.helpers import (
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

	import user
	import config

	# Verify or query parameters
	if not user.valid_username(args.username):
		config.logger.error("Invalid username: usernames may only contain alphanumeric characters, dashes, and underscores")
		return -1
	if user.UserModel.by(name=args.username) is not None:
		config.logger.error("Invalid username: username is already taken")
		return -1
	if not args.displayname:
		args.displayname = args.username
	if not user.valid_email(args.email):
		config.logger.error("Invalid email")
		return -1

	# Create user
	new_user, tmp_pw = user.create_user(args.username, args.displayname, args.email)
	with config.json_ro(new_user.config_path) as js:
		print(json.dumps(js, indent=2))
	print("Username: {}\nUser ID:  {}\nPassword: {}".format(args.username, new_user.uid, tmp_pw))

@add_argument("--id", required=True, help="id of user to delete")
def command_delete(args):
	"""
	Delete a user
	"""
	import os

	import config

	user_path = config.prepend('user', args.uid)
	if not os.path.isdir(user_path):
		config.logger.error("No user with that id")
		return -1
	else:
		os.remove(user_path)
	with config.json_rw('user', 'index.json') as j:
		if args.uid in j:
			del j[uid]

@no_argument
def command_list(args):
	"""List all users"""
	import os

	import config

	user_dirs = os.listdir(config.prepend('user'))
	users = []
	for uid in user_dirs:
		if uid == "index.json": continue
		with config.json_ro('user', uid, 'config.json') as user:
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
	import config
	from user import UserModel

	if args.get and args.set:
		config.logger.error("Specify one of --get and --set")
		return -1

	u = UserModel.by(name=args.username)
	if not u:
		config.logger.error("User not found")
		return -1

	if args.get:
		with config.json_ro('user', u.id, 'config.json') as cfg:
			config_get(cfg, args.get)

	if args.set:
		with config.json_rw('user', u.id, 'config.json') as cfg:
			config_set(cfg, args.set)

@add_argument("--username", help="The user to change password for")
def command_passwd(args):
	"""
	Set a user's password
	"""
	import getpass
	import os

	import config
	from user import UserModel

	if not args.username:
		args.username = input("Username: ")
	u = UserModel.by(name=args.username)
	if u is None:
		config.logger.error("No user with username '{}'".format(args.username))
		return -1
	pw = getpass.getpass("Password: ")
	u.set_password(pw)
