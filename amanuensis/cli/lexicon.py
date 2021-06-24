import logging

from sqlalchemy import update

import amanuensis.backend.lexicon as lexiq
import amanuensis.backend.membership as memq
import amanuensis.backend.user as userq
from amanuensis.db import DbContext, Lexicon

from .helpers import add_argument


COMMAND_NAME = "lexicon"
COMMAND_HELP = "Interact with lexicons."

LOG = logging.getLogger(__name__)


@add_argument("lexicon")
@add_argument("user")
@add_argument("--editor", action="store_true")
def command_add(args) -> int:
    """
    Add a user to a lexicon.
    """
    db: DbContext = args.get_db()
    lexicon = lexiq.from_name(db, args.lexicon)
    user = userq.from_username(db, args.user)
    assert user is not None
    memq.create(db, user.id, lexicon.id, args.editor)
    LOG.info(f"Added {args.user} to lexicon {args.lexicon}")
    return 0


@add_argument("name")
def command_create(args):
    """
    Create a lexicon.
    """
    db: DbContext = args.get_db()
    lexiq.create(db, args.name, None, f"Prompt for Lexicon {args.name}")
    LOG.info(f"Created lexicon {args.name}")
    return 0


@add_argument("name")
@add_argument("--public", dest="public", action="store_const", const=True)
@add_argument("--no-public", dest="public", action="store_const", const=False)
@add_argument("--join", dest="join", action="store_const", const=True)
@add_argument("--no-join", dest="join", action="store_const", const=False)
def command_edit(args):
    """
    Update a lexicon's configuration.
    """
    db: DbContext = args.get_db()
    values = {}

    if args.public == True:
        values["public"] = True
    elif args.public == False:
        values["public"] = False

    if args.join == True:
        values["joinable"] = True
    elif args.join == False:
        values["joinable"] = False

    result = db(update(Lexicon).where(Lexicon.name == args.name).values(**values))
    LOG.info(f"Updated {result.rowcount} lexicons")
    db.session.commit()
    return 0 if result.rowcount == 1 else -1
