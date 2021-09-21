import logging

from amanuensis.backend import *
from amanuensis.db import *

from .helpers import add_argument


COMMAND_NAME = "post"
COMMAND_HELP = "Interact with posts."

LOG = logging.getLogger(__name__)


@add_argument("--lexicon", required=True, help="The lexicon's name")
@add_argument("--by", help="The character's public id")
@add_argument("--text", help="The text of the post")
def command_create(args) -> int:
    """
    Create a post in a lexicon.
    """
    db: DbContext = args.get_db()
    lexicon = lexiq.try_from_name(db, args.lexicon)
    if not lexicon:
        raise ValueError("Lexicon does not exist")
    user = userq.try_from_username(db, args.by)
    user_id = user.id if user else None
    post: Post = postq.create(db, lexicon.id, user_id, args.text)
    preview = post.body[:20] + "..." if len(post.body) > 20 else post.body
    LOG.info(f"Posted '{preview}' in {lexicon.full_title}")
    return 0
