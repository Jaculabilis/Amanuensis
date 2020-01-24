"""
Functions for managing lexicons, primarily within the context of the
Amanuensis config directory.
"""
import json
import os
import re
import shutil
import time
import uuid

from amanuensis.config import prepend, json_rw, json_ro, logger
from amanuensis.config.loader import AttrOrderedDict
from amanuensis.lexicon import LexiconModel
from amanuensis.resources import get_stream

def valid_name(name):
	"""
	Validates that a lexicon name consists only of alpahnumerics, dashes,
	underscores, and spaces
	"""
	return name is not None and re.match(r"^[A-Za-z0-9-_ ]+$", name) is not None


def create_lexicon(name, editor):
	"""
	Creates a lexicon with the given name and sets the given user as its editor
	"""
	# Verify arguments
	if not valid_name(name):
		raise ValueError("Invalid lexicon name: '{}'".format(name))
	if editor is None:
		raise ValueError("Invalid editor: '{}'".format(editor))

	# Create the lexicon directory and initialize it with a blank lexicon
	lid = uuid.uuid4().hex
	lex_dir = prepend("lexicon", lid)
	os.mkdir(lex_dir)
	with get_stream("lexicon.json") as s:
		with open(prepend(lex_dir, 'config.json'), 'wb') as f:
			f.write(s.read())

	# Fill out the new lexicon
	with json_rw(lex_dir, 'config.json') as cfg:
		cfg['lid'] = lid
		cfg['name'] = name
		cfg['editor'] = editor.uid
		cfg['time']['created'] = int(time.time())

	# Update the index with the new lexicon
	with json_rw('lexicon', 'index.json') as index:
		index[name] = lid

	# Load the Lexicon and log creation
	l = LexiconModel(lid)
	l.log("Lexicon created")

	logger.info("Created Lexicon {0.name}, ed. {1.displayname} ({0.id})".format(
		l, editor))

	# Add the editor
	add_player(l, editor)

	# Add the fallback character
	add_character(l, editor, {
		"cid": "default",
		"name": "Ersatz Scrivener",
		"player": None,
	})

	return l


def delete_lexicon(lex, purge=False):
	"""
	Deletes the given lexicon from the internal configuration

	Does not delete the lexicon from the data folder unless purge=True.
	"""
	# Verify arguments
	if lex is None:
		raise ValueError("Invalid lexicon: '{}'".format(lex))
	
	# Delete the lexicon from the index
	with json_rw('lexicon', 'index.json') as j:
		if lex.id in j:
			del j[lex.id]

	# Delete the lexicon data folder if purging
	if purge:
		raise NotImplementedError()

	# Delete the lexicon config
	lex_path = prepend('lexicon', lex.id)
	shutil.rmtree(lex_path)


def get_all_lexicons():
	"""
	Loads each lexicon in the lexicon index
	"""
	# Get all the lexicon ids in the index
	with json_ro('lexicon', 'index.json') as index:
		lids = list(index.values())

	# Load all of the lexicons
	lexes = list(map(lambda id: LexiconModel.by(lid=id), lids))

	return lexes


def valid_add(lex, player, password=None):
	"""
	Checks whether the given player can join a lexicon
	"""
	# Trivial failures
	if lex is None:
		return False
	if player is None:
		return False
	# Can't join if already in the game
	if player.id in lex.join.joined:
		return False
	# Can't join if the game is closed
	if not lex.join.open:
		return False
	# Can't join if the player max is reached
	if len(lex.join.joined) >= lex.join.max_players:
		return False
	# Can't join if the password doesn't check out
	if lex.join.password is not None and lex.join.password != password:
		return False

	return True


def add_player(lex, player):
	"""
	Unconditionally adds a player to a lexicon
	"""
	# Verify arguments
	if lex is None:
		raise ValueError("Invalid lexicon: '{}'".format(lex))
	if player is None:
		raise ValueError("Invalid player: '{}'".format(player))

	# Idempotently add player
	added = False
	with json_rw(lex.config_path) as cfg:
		if player.id not in cfg.join.joined:
			cfg.join.joined.append(player.id)
			added = True
	
	# Log to the lexicon's log
	if added:
		lex.log("Player '{0.username}' joined ({0.id})".format(player))


def remove_player(lex, player):
	"""
	Remove a player from a lexicon
	"""
	# Verify arguments
	if lex is None:
		raise ValueError("Invalid lexicon: '{}'".format(lex))
	if player is None:
		raise ValueError("Invalid player: '{}'".format(player))
	if lex.editor == player.id:
		raise ValueError("Can't remove the editor '{}' from lexicon '{}'".format(player.username, lex.name))

	# Idempotently remove player
	with json_rw(lex.config_path) as cfg:
		if player.id in cfg.join.joined:
			cfg.join.joined.remove(player.id)

	# TODO Reassign the player's characters to the editor


def add_character(lex, player, charinfo={}):
	"""
	Unconditionally adds a character to a lexicon

	charinfo is a dictionary of character settings
	"""
	# Verify arguments
	if lex is None:
		raise ValueError("Invalid lexicon: '{}'".format(lex))
	if player is None:
		raise ValueError("Invalid player: '{}'".format(player))
	if not charinfo or not charinfo.get("name"):
		raise ValueError("Invalid character info: '{}'".format(charinfo))
	charname = charinfo.get("name")
	if any([char.name for char in lex.character.values() if char.name == charname]):
		raise ValueError("Duplicate character name: '{}'".format(charinfo))

	# Load the character template
	with get_stream('character.json') as template:
		character = json.load(template, object_pairs_hook=AttrOrderedDict)

	# Fill out the character's information
	character.cid = charinfo.get("cid") or uuid.uuid4().hex
	character.name = charname
	character.player = charinfo.get("player") or player.id
	character.signature = charinfo.get("signature") or ("~" + character.name)

	# Add the character to the lexicon
	added = False
	with json_rw(lex.config_path) as cfg:
		cfg.character.new(character.cid, character)
		added = True

	# Log addition
	if added:
			lex.log("Character '{0.name}' created ({0.cid})".format(character))

def delete_character(lex, charname):
	"""
	Delete a character from a lexicon
	"""
	# Verify arguments
	if lex is None:
		raise ValueError("Invalid lexicon: '{}'".format(lex))
	if charname is None:
		raise ValueError("Invalid character name: '{}'".format(charinfo))

	# Find character in this lexicon
	matches = [char for cid, char in lex.character.items() if char.name == charname]
	if len(matches) != 1:
		raise ValueError(matches)
	char = matches[0]

	# Remove character from character list
	with json_rw(lex.config_path) as cfg:
		del cfg.character[char.cid]