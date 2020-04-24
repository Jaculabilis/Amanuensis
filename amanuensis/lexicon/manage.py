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
from amanuensis.errors import ArgumentError
from amanuensis.lexicon import LexiconModel
from amanuensis.parser import parse_raw_markdown, GetCitations, HtmlRenderer, filesafe_title, titlesort
from amanuensis.resources import get_stream





def delete_lexicon(lex, purge=False):
	"""
	Deletes the given lexicon from the internal configuration

	Does not delete the lexicon from the data folder unless purge=True.
	"""
	# Verify arguments
	if lex is None:
		raise ArgumentError("Invalid lexicon: '{}'".format(lex))

	# Delete the lexicon from the index
	with json_rw('lexicon', 'index.json') as index:
		if lex.name in index:
			del index[lex.name]

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


def get_user_lexicons(user):
	"""
	Loads each lexicon that the given user is a player in
	"""
	return [
		lexicon
		for lexicon in get_all_lexicons()
		if user.in_lexicon(lexicon)]


def remove_player(lex, player):
	"""
	Remove a player from a lexicon
	"""
	# Verify arguments
	if lex is None:
		raise ArgumentError("Invalid lexicon: '{}'".format(lex))
	if player is None:
		raise ArgumentError("Invalid player: '{}'".format(player))
	if lex.editor == player.id:
		raise ArgumentError(
			"Can't remove the editor '{}' from lexicon '{}'".format(
				player.username, lex.name))

	# Idempotently remove player
	with json_rw(lex.config_path) as cfg:
		if player.id in cfg.join.joined:
			cfg.join.joined.remove(player.id)

	# TODO Reassign the player's characters to the editor


def delete_character(lex, charname):
	"""
	Delete a character from a lexicon
	"""
	# Verify arguments
	if lex is None:
		raise ArgumentError("Invalid lexicon: '{}'".format(lex))
	if charname is None:
		raise ArgumentError("Invalid character name: '{}'".format(charname))

	# Find character in this lexicon
	matches = [
		char for cid, char in lex.character.items()
		if char.name == charname]
	if len(matches) != 1:
		raise ArgumentError(matches)
	char = matches[0]

	# Remove character from character list
	with json_rw(lex.config_path) as cfg:
		del cfg.character[char.cid]

