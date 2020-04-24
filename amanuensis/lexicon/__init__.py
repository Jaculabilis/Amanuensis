from amanuensis.lexicon.admin import valid_name, create_lexicon
from amanuensis.lexicon.setup import (
	player_can_join_lexicon,
	add_player_to_lexicon)

__all__ = [member.__name__ for member in [
	valid_name,
	create_lexicon,
	player_can_join_lexicon,
	add_player_to_lexicon,
]]
