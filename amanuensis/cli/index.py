import enum
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
