# Standard library imports
import getpass
import logging
# import shutil

# Module imports
from amanuensis.models import UserModel

from .helpers import (
	add_argument,
	no_argument,
	requires_user,
	alias,
	config_get,
	config_set,
	CONFIG_GET_ROOT_VALUE)

logger = logging.getLogger(__name__)


@alias('uc')
@add_argument("--username", required=True, help="Name of user to create")
@add_argument("--email", help="User's email")
@add_argument("--displayname", help="User's publicly displayed name")
def command_create(args):
	"""
	Create a user
	"""
	# Module imports
	from amanuensis.user import (
		valid_username, valid_email, create_user)

	# Verify arguments
	if not valid_username(args.username):
		logger.error("Invalid username: usernames may only contain alphanumer"
			"ic characters, dashes, and underscores")
		return -1
	if not args.displayname:
		args.displayname = args.username
	if args.email and not valid_email(args.email):
		logger.error("Invalid email")
		return -1
	try:
		existing_user = args.model_factory.user(args.username)
		if existing_user is not None:
			logger.error("Invalid username: username is already taken")
			return -1
	except Exception:
		pass  # User doesn't already exist, good to go

	# Perform command
	new_user, tmp_pw = create_user(
		args.root,
		args.model_factory,
		args.username,
		args.displayname,
		args.email)

	# Output
	print(tmp_pw)
	return 0


@alias('ud')
@requires_user
def command_delete(args):
	"""
	Delete a user
	"""
	raise NotImplementedError()
	# # Module imports
	# from amanuensis.config import logger, prepend, json_rw

	# # Perform command
	# user_path = prepend('user', args.user.id)
	# shutil.rmtree(user_path)
	# with json_rw('user', 'index.json') as index:
	# 	del index[args.user.username]

	# # TODO resolve user id references in all games

	# # Output
	# logger.info("Deleted user {0.username} ({0.id})".format(args.user))
	# return 0


@alias('ul')
@no_argument
def command_list(args):
	"""List all users"""
	raise NotImplementedError()
	# # Module imports
	# from amanuensis.config import prepend, json_ro
	# from amanuensis.user import UserModel

	# # Perform command
	# users = []
	# with json_ro('user', 'index.json') as index:
	# 	for username, uid in index.items():
	# 		users.append(UserModel.by(uid=uid))

	# # Output
	# users.sort(key=lambda u: u.username)
	# for user in users:
	# 	print("{0.id}  {0.displayname} ({0.username})".format(user))
	# return 0


@alias('un')
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
	user: UserModel = args.user

	# Verify arguments
	if args.get and args.set:
		logger.error("Specify one of --get and --set")
		return -1

	# Perform command
	if args.get:
		config_get(user.cfg, args.get)

	if args.set:
		with user.ctx.edit_config() as cfg:
			config_set(user.uid, cfg, args.set)

	# Output
	return 0


@alias('up')
@requires_user
@add_argument("--password", help="The password to set. Used for scripting; "
	"not recommended for general use")
def command_passwd(args):
	"""
	Set a user's password
	"""
	user: UserModel = args.user

	# Verify arguments
	password: str = args.password or getpass.getpass("Password: ")

	# Perform command
	user.set_password(password)

	# Output
	logger.info('Updated password for {}'.format(user.cfg.username))
	return 0
