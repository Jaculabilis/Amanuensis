"""
Submodule of functions for managing lexicon games during the setup and
joining part of the game lifecycle.
"""
from amanuensis.errors import ArgumentError
from amanuensis.models import LexiconModel, UserModel


def player_can_join_lexicon(
	player: UserModel,
	lexicon: LexiconModel,
	password: str = None):
	"""
	Checks whether the given player can join a lexicon
	"""
	# Trivial failures
	if lexicon is None:
		return False
	if player is None:
		return False
	# Can't join if already in the game
	if player.uid in lexicon.cfg.join.joined:
		return False
	# Can't join if the game is closed
	if not lexicon.cfg.join.open:
		return False
	# Can't join if there's no room left
	if len(lexicon.cfg.join.joined) >= lexicon.cfg.join.max_players:
		return False
	# Can't join if the password doesn't check out
	if (lexicon.cfg.join.password is not None
		and lexicon.cfg.join.password != password):
		return False
	return True


def add_player_to_lexicon(
	player: UserModel,
	lexicon: LexiconModel):
	"""
	Unconditionally adds a player to a lexicon
	"""
	# Verify arguments
	if lexicon is None:
		raise ArgumentError(f'Invalid lexicon: {lexicon}')
	if player is None:
		raise ArgumentError(f'Invalid player: {player}')

	# Idempotently add player
	added = False
	with lexicon.ctx.edit_config() as cfg:
		if player.uid not in cfg.join.joined:
			cfg.join.joined.append(player.uid)
			added = True

	# Log to the lexicon's log
	if added:
		lexicon.log('Player "{0.cfg.username}" joined ({0.uid})'.format(player))
