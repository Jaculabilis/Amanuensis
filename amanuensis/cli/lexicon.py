from amanuensis.cli.helpers import (
	add_argument, no_argument, requires_lexicon, requires_user,
	config_get, config_set, CONFIG_GET_ROOT_VALUE)

#
# CRUD commands
#

@add_argument("--name", required=True, help="The name of the new lexicon")
@requires_user
@add_argument("--prompt", help="The lexicon's prompt")
def command_create(args):
	"""
	Create a lexicon

	The specified user will be the editor. A newly created created lexicon is
	not open for joining and requires additional configuration before it is
	playable. The editor should ensure that all settings are as desired before
	opening the lexicon for player joins.
	"""
	# Module imports
	from amanuensis.config import logger, json_ro
	from amanuensis.lexicon.manage import valid_name, create_lexicon

	# Verify arguments
	if not valid_name(args.name):
		logger.error("Lexicon name contains illegal characters: '{}'".format(
			args.name))
		return -1
	with json_ro('lexicon', 'index.json') as index:
		if args.name in index.keys():
			logger.error('A lexicon with name "{}" already exists'.format(
				args.name))
			return -1

	# Perform command
	lexicon = create_lexicon(args.name, args.user)

	# Output already logged by create_lexicon
	return 0


@requires_lexicon
@add_argument("--purge", action="store_true", help="Delete the lexicon's data")
def command_delete(args):
	"""
	Delete a lexicon and optionally its data
	"""
	# Module imports
	from amanuensis.config import logger
	from amanuensis.lexicon import LexiconModel
	from amanuensis.lexicon.manage import delete_lexicon

	# Perform command
	delete_lexicon(args.lexicon, args.purge)

	# Output
	logger.info('Deleted lexicon "{}"'.format(args.lexicon.name))
	return 0


@no_argument
def command_list(args):
	"""
	List all lexicons and their statuses
	"""
	# Module imports
	from amanuensis.lexicon.manage import get_all_lexicons

	# Execute command
	lexicons = get_all_lexicons()

	# Output
	statuses = []
	for lex in lexicons:
		statuses.append("{0.lid}  {0.name} ({1})".format(lex, lex.status()))
	for s in statuses:
		print(s)
	return 0


@requires_lexicon
@add_argument(
	"--get", metavar="PATHSPEC", dest="get",
	nargs="?", const=CONFIG_GET_ROOT_VALUE,
	help="Get the value of a config key")
@add_argument(
	"--set", metavar=("PATHSPEC", "VALUE"), dest="set",
	nargs=2, help="Set the value of a config key")
def command_config(args):
	"""
	Interact with a lexicon's config
	"""
	# Module imports
	from amanuensis.config import logger, json_ro, json_rw
	from amanuensis.lexicon import LexiconModel

	# Verify arguments
	if args.get and args.set:
		logger.error("Specify one of --get and --set")
		return -1

	# Execute command
	if args.get:
		config_get(args.lexicon.config, args.get)

	if args.set:
		with json_rw(args.lexicon.config_path) as cfg:
			config_set(args.lexicon.id, cfg, args.set)

	# config_* functions handle output
	return 0

#
# Player/character commands
#

@requires_lexicon
# @requires_username
def command_player_add(args):
	"""
	Add a player to a lexicon
	"""
	# Module imports
	from amanuensis.config import logger
	from amanuensis.lexicon import LexiconModel
	from amanuensis.lexicon.manage import add_player
	from amanuensis.user import UserModel

	# Verify arguments
	u = UserModel.by(name=args.username)
	if u is None:
		logger.error("Could not find user '{}'".format(args.username))
		return -1
	lex = LexiconModel.by(name=args.lexicon)
	if lex is None:
		logger.error("Could not find lexicon '{}'".format(args.lexicon))
		return -1

	# Internal call
	add_player(lex, u)
	return 0


@requires_lexicon
# @requires_username
def command_player_remove(args):
	"""
	Remove a player from a lexicon

	Removing a player dissociates them from any characters
	they control but does not delete any character data.
	"""
	# Module imports
	from amanuensis.config import logger
	from amanuensis.lexicon import LexiconModel
	from amanuensis.lexicon.manage import remove_player
	from amanuensis.user import UserModel

	# Verify arguments
	u = UserModel.by(name=args.username)
	if u is None:
		logger.error("Could not find user '{}'".format(args.username))
		return -1
	lex = LexiconModel.by(name=args.lexicon)
	if lex is None:
		logger.error("Could not find lexicon '{}'".format(args.lexicon))
		return -1
	if lex.editor == u.id:
		logger.error("Can't remove the editor of a lexicon")
		return -1

	# Internal call
	remove_player(lex, u)
	return 0


@requires_lexicon
def command_player_list(args):
	"""
	List all players in a lexicon
	"""
	import json
	# Module imports
	from amanuensis.config import logger
	from amanuensis.lexicon import LexiconModel
	from amanuensis.user import UserModel

	# Verify arguments
	lex = LexiconModel.by(name=args.lexicon)
	if lex is None:
		logger.error("Could not find lexicon '{}'".format(args.lexicon))
		return -1

	# Internal call
	players = []
	for uid in lex.join.joined:
		u = UserModel.by(uid=uid)
		players.append(u.username)

	print(json.dumps(players, indent=2))
	return 0


@requires_lexicon
# @requires_username
@add_argument("--charname", required=True, help="The character's name")
def command_char_create(args):
	"""
	Create a character for a lexicon

	The specified player will be set as the character's player.
	"""
	# Module imports
	from amanuensis.config import logger
	from amanuensis.lexicon import LexiconModel
	from amanuensis.lexicon.manage import add_character
	from amanuensis.user import UserModel

	# Verify arguments
	u = UserModel.by(name=args.username)
	if u is None:
		logger.error("Could not find user '{}'".format(args.username))
		return -1
	lex = LexiconModel.by(name=args.lexicon)
	if lex is None:
		logger.error("Could not find lexicon '{}'".format(args.lexicon))
		return -1
	# u in lx TODO

	# Internal call
	add_character(lex, u, {"name": args.charname})
	return 0


@requires_lexicon
@add_argument("--charname", required=True, help="The character's name")
def command_char_delete(args):
	"""
	Delete a character from a lexicon

	Deleting a character dissociates them from any content
	they have contributed rather than deleting it.
	"""
	# Module imports
	from amanuensis.config import logger
	from amanuensis.lexicon import LexiconModel
	from amanuensis.lexicon.manage import delete_character

	# Verify arguments
	lex = LexiconModel.by(name=args.lexicon)
	if lex is None:
		logger.error("Could not find lexicon '{}'".format(args.lexicon))
		return -1

	# Internal call
	delete_character(lex, args.charname)
	return 0

@requires_lexicon
def command_char_list(args):
	"""
	List all characters in a lexicon
	"""
	import json
	# Module imports
	from amanuensis.config import logger
	from amanuensis.lexicon import LexiconModel

	# Verify arguments
	lex = LexiconModel.by(name=args.lexicon)
	if lex is None:
		logger.error("Could not find lexicon '{}'".format(args.lexicon))
		return -1

	# Internal call
	print(json.dumps(lex.character, indent=2))
	return 0

#
# Procedural commands
#

@requires_lexicon
@add_argument(
	"--as-deadline", action="store_true",
	help="Notifies players of the publish result")
@add_argument(
	"--force", action="store_true",
	help="Publish all approved articles, regardless of other checks")
def command_publish_turn(args):
	"""
	Publishes the current turn of a lexicon

	The --as-deadline flag is intended to be used only by the scheduled publish
	attempts controlled by the publish.deadlines setting.

	The --force flag bypasses the publish.quorum and publish.block_on_ready
	settings.
	"""
	# Module imports

	raise NotImplementedError() # TODO
