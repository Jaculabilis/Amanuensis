from cli.helpers import add_argument, no_argument, requires

#
# CRUD commands
#

@no_argument
@requires("lexicon")
def command_create(args):
	"""
	Create a lexicon
	"""
	raise NotImplementedError()

@no_argument
@requires("lexicon")
def command_delete(args):
	"""
	Delete a lexicon and all its data
	"""
	raise NotImplementedError()

@no_argument
def command_list(args):
	"""
	List all lexicons and their statuses
	"""
	raise NotImplementedError()

@no_argument
@requires("lexicon")
def command_config(args):
	"""
	Interact with a lexicon's config
	"""
	raise NotImplementedError()

#
# Player/character commands
#

@no_argument
@requires("lexicon")
def command_player_add(args):
	"""
	Add a player to a lexicon
	"""
	raise NotImplementedError()

@no_argument
@requires("lexicon")
def command_player_remove(args):
	"""
	Remove a player from a lexicon

	Removing a player dissociates them from any characters
	they control but does not delete any character data.
	"""
	raise NotImplementedError()

@no_argument
@requires("lexicon")
def command_player_list(args):
	"""
	List all players in a lexicon
	"""
	raise NotImplementedError()

@no_argument
@requires("lexicon")
def command_char_create(args):
	"""
	Create a character for a lexicon
	"""
	raise NotImplementedError()

@no_argument
@requires("lexicon")
def command_char_delete(args):
	"""
	Delete a character from a lexicon

	Deleting a character dissociates them from any content
	they have contributed rather than deleting it.
	"""
	raise NotImplementedError()

@no_argument
@requires("lexicon")
def command_char_list(args):
	"""
	List all characters in a lexicon
	"""
	raise NotImplementedError()

#
# Procedural commands
#

@no_argument
@requires("lexicon")
def command_publish_turn(args):
	"""
	Publishes the current turn of a lexicon

	Ability to publish is checked against the lexicon's
	turn publish policy unless --force is specified.
	"""
	raise NotImplementedError()