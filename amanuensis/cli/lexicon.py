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
	from lexicon.manage import create_lexicon
	import user
	# TODO verify args
	uid = user.uid_from_username(args.editor)
	u = user.user_from_uid(uid)
	create_lexicon(args.name, u)

@requires_lexicon
def command_delete(args):
	"""
	Delete a lexicon and all its data
	"""
	raise NotImplementedError() # TODO

@no_argument
def command_list(args):
	"""
	List all lexicons and their statuses
	"""
	raise NotImplementedError() # TODO

@requires_lexicon
def command_config(args):
	"""
	Interact with a lexicon's config
	"""
	raise NotImplementedError() # TODO

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