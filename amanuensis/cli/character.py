import logging

from amanuensis.backend import lexiq, userq, charq
from amanuensis.db import DbContext, Character

from .helpers import add_argument


COMMAND_NAME = "char"
COMMAND_HELP = "Interact with characters."

LOG = logging.getLogger(__name__)


@add_argument("--lexicon", required=True)
@add_argument("--user", required=True)
@add_argument("--name", required=True)
def command_create(args) -> int:
    """
    Create a character.
    """
    db: DbContext = args.get_db()
    lexicon = lexiq.try_from_name(db, args.lexicon)
    if not lexicon:
        raise ValueError("Lexicon does not exist")
    user = userq.try_from_username(db, args.user)
    if not user:
        raise ValueError("User does not exist")
    char: Character = charq.create(db, lexicon.id, user.id, args.name, signature=None)
    LOG.info(f"Created {char.name} in {lexicon.full_title}")
    return 0
