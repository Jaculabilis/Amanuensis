"""
Submodule of functions for managing lexicon games during the setup and
joining part of the game lifecycle.
"""
import json
import uuid

from amanuensis.config import AttrOrderedDict
from amanuensis.errors import ArgumentError
from amanuensis.models import LexiconModel, UserModel
from amanuensis.resources import get_stream


def player_can_create_character(
	player: UserModel,
	lexicon: LexiconModel,
	name: str) -> bool:
	"""
	Checks whether a player can create a character with the given name
	"""
	# Trivial failures
	if not player or not lexicon or not name:
		return False
	# User needs to be a player
	if player.uid not in lexicon.cfg.join.joined:
		return False
	# Character can't be a dupe
	if any([
			char.name for char in lexicon.cfg.character.values()
			if char.name == name]):
		return False
	# Player can't add more characters than the limit
	if len([
			char for char in lexicon.cfg.character.values()
			if char.player == player.uid]) > lexicon.cfg.join.chars_per_player:
		return False
	# Players can't add characters after the game has started
	if lexicon.cfg.turn.current:
		return False
	return True


def create_character_in_lexicon(
	player: UserModel,
	lexicon: LexiconModel,
	name: str) -> str:
	"""
	Unconditionally creates a character for a player
	"""
	# Verify arguments
	if lexicon is None:
		raise ArgumentError(f'Invalid lexicon: {lexicon}')
	if player is None:
		raise ArgumentError(f'Invalid player: {player}')
	if player.uid not in lexicon.cfg.join.joined:
		raise ArgumentError(f'Player {player} not in lexicon {lexicon}')
	if not name:
		raise ArgumentError(f'Invalid character name: "{name}"')
	if any([
			char.name for char in lexicon.cfg.character.values()
			if char.name == name]):
		raise ArgumentError(f'Duplicate character name: "{name}"')

	# Load the character template
	with get_stream('character.json') as template:
		character = json.load(template, object_pairs_hook=AttrOrderedDict)

	# Fill out the character's information
	character.cid = uuid.uuid4().hex
	character.name = name
	character.player = player.uid
	character.signature = "~" + character.name

	# Add the character to the lexicon
	with lexicon.ctx.edit_config() as cfg:
		cfg.character.new(character.cid, character)

	# Log addition
	lexicon.log(f'Character "{name}" created ({character.cid})')

	return character.cid
