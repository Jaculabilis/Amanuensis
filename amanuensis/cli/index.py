import logging

from amanuensis.backend import *
from amanuensis.db import DbContext, ArticleIndex, IndexType

from .helpers import add_argument


COMMAND_NAME = "index"
COMMAND_HELP = "Interact with indices."

LOG = logging.getLogger(__name__)


@add_argument("--lexicon", required=True)
@add_argument(
    "--type", required=True, type=lambda s: IndexType[s.upper()], choices=IndexType
)
@add_argument("--pattern", required=True)
@add_argument("--logical", type=int, default=0)
@add_argument("--display", type=int, default=0)
@add_argument("--capacity", type=int, default=None)
def command_create(args) -> int:
    """
    Create an index for a lexicon.
    """
    db: DbContext = args.get_db()
    lexicon = lexiq.try_from_name(db, args.lexicon)
    if not lexicon:
        raise ValueError("Lexicon does not exist")
    index: ArticleIndex = indq.create(
        db,
        lexicon.id,
        args.type,
        args.pattern,
        args.logical,
        args.display,
        args.capacity,
    )
    LOG.info(f"Created {index.index_type}:{index.pattern} in {lexicon.full_title}")
    return 0


@add_argument("--lexicon", required=True, help="The lexicon's name")
@add_argument("--character", help="The character's public id")
@add_argument("--index", required=True, help="The index pattern")
@add_argument("--turn", required=True, type=int)
def command_assign(args) -> int:
    """
    Create a turn assignment for a lexicon.
    """
    db: DbContext = args.get_db()
    lexicon = lexiq.try_from_name(db, args.lexicon)
    if not lexicon:
        raise ValueError("Lexicon does not exist")
    char = charq.try_from_public_id(db, args.character)
    assert char
    indices = indq.get_for_lexicon(db, lexicon.id)
    index = [i for i in indices if i.pattern == args.index]
    if not index:
        raise ValueError("Index not found")
    assignment = irq.create(db, lexicon.id, char.id, index[0].id, args.turn)
    LOG.info("Created")
    return 0
