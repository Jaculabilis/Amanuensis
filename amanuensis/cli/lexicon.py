from cli.helpers import (
	add_argument, no_argument, requires_lexicon, requires_username,
	config_get, config_set, CONFIG_GET_ROOT_VALUE)

#
# CRUD commands
#

@requires_lexicon
@add_argument("--editor", "-e", required=True, help="Name of the user who will be editor")
def command_create(args):
	"""
	Create a lexicon

	A newly created lexicon is not open for joining and requires additional
	configuration before it is playable. The editor should ensure that all
	settings are as desired before opening the lexicon for player joins.
	"""
	# Module imports
	from config import logger
	from lexicon.manage import valid_name, create_lexicon
	from user import UserModel

	# Verify arguments
	if not valid_name(args.lexicon):
		logger.error("Lexicon name contains illegal characters: '{}'".format(
			args.lexicon))
		return -1
	editor = UserModel.by(name=args.editor)
	if editor is None:
		logger.error("Could not find user '{}'".format(args.editor))
		return -1

	# Internal call
	create_lexicon(args.lexicon, editor)


@requires_lexicon
@add_argument("--purge", action="store_true", help="Delete the lexicon's data")
def command_delete(args):
	"""
	Delete a lexicon and optionally its data
	"""
	# Module imports
	from config import logger
	from lexicon import LexiconModel
	from lexicon.manage import delete_lexicon

	# Verify arguments
	lex = LexiconModel.by(name=args.lexicon)
	if lex is None:
		logger.error("Could not find lexicon '{}'".format(args.lexicon))
		return -1

	# Internal call
	delete_lexicon(lex, args.purge)
	logger.info("Deleted lexicon '{}'".format(args.lexicon))


@no_argument
def command_list(args):
	"""
	List all lexicons and their statuses
	"""
	# Module imports
	from lexicon.manage import get_all_lexicons

	# Internal call
	lexicons = get_all_lexicons()
	statuses = []
	for lex in lexicons:
		if lex.turn['current'] is None:
			statuses.append("{0.lid}  {0.name} ({1})".format(lex, "Unstarted"))
		elif lex.turn['current'] > lex.turn['max']:
			statuses.append("{0.lid}  {0.name} ({1})".format(lex, "Completed"))
		else:
			statuses.append("{0.lid}  {0.name} (Turn {1}/{2})".format(lex, lex.turn['current'], lex.turn['max']))
	for s in statuses:
		print(s)


@requires_lexicon
@add_argument(
	"--get", metavar="PATHSPEC", dest="get",
	nargs="?", const=CONFIG_GET_ROOT_VALUE, help="Get the value of a config key")
@add_argument(
	"--set", metavar=("PATHSPEC", "VALUE"), dest="set",
	nargs=2, help="Set the value of a config key")
def command_config(args):
	"""
	Interact with a lexicon's config
	"""
	# Module imports
	from config import logger, json_ro, json_rw
	from lexicon import LexiconModel

	# Verify arguments
	if args.get and args.set:
		logger.error("Specify one of --get and --set")
		return -1
	lex = LexiconModel.by(name=args.lexicon)
	if lex is None:
		logger.error("Could not find lexicon '{}'".format(args.lexicon))
		return -1

	# Internal call
	if args.get:
		with json_ro(lex.config_path) as cfg:
			config_get(cfg, args.get)

	if args.set:
		with json_rw(lex.config_path) as cfg:
			config_set(cfg, args.set)

#
# Player/character commands
#

@requires_lexicon
@requires_username
def command_player_add(args):
	"""
	Add a player to a lexicon
	"""
	raise NotImplementedError() # TODO

@requires_lexicon
@requires_username
def command_player_remove(args):
	"""
	Remove a player from a lexicon

	Removing a player dissociates them from any characters
	they control but does not delete any character data.
	"""
	raise NotImplementedError() # TODO

@requires_lexicon
@requires_username
def command_player_list(args):
	"""
	List all players in a lexicon
	"""
	raise NotImplementedError() # TODO

@requires_lexicon
def command_char_create(args):
	"""
	Create a character for a lexicon
	"""
	raise NotImplementedError() # TODO

@requires_lexicon
def command_char_delete(args):
	"""
	Delete a character from a lexicon

	Deleting a character dissociates them from any content
	they have contributed rather than deleting it.
	"""
	raise NotImplementedError() # TODO

@requires_lexicon
def command_char_list(args):
	"""
	List all characters in a lexicon
	"""
	raise NotImplementedError() # TODO

#
# Procedural commands
#

@requires_lexicon
def command_publish_turn(args):
	"""
	Publishes the current turn of a lexicon

	Ability to publish is checked against the lexicon's
	turn publish policy unless --force is specified.
	"""
	raise NotImplementedError() # TODO