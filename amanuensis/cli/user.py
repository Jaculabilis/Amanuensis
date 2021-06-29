import logging
from typing import Optional

from amanuensis.backend import userq
from amanuensis.db import DbContext, User

from .helpers import add_argument


COMMAND_NAME = "user"
COMMAND_HELP = "Interact with users."

LOG = logging.getLogger(__name__)


@add_argument("username")
@add_argument("--password", default="password")
@add_argument("--email", default="")
def command_create(args) -> int:
    """Create a user."""
    db: DbContext = args.get_db()
    userq.create(db, args.username, "password", args.username, args.email, False)
    userq.password_set(db, args.username, args.password)
    LOG.info(f"Created user {args.username}")
    return 0


@add_argument("username")
def command_promote(args) -> int:
    """Make a user a site admin."""
    db: DbContext = args.get_db()
    user: Optional[User] = userq.try_from_username(db, args.username)
    if user is None:
        args.parser.error("User not found")
        return -1
    if user.is_site_admin:
        LOG.info(f"{user.username} is already a site admin.")
    else:
        user.is_site_admin = True
        LOG.info(f"Promoting {user.username} to site admin.")
        db.session.commit()
    return 0


@add_argument("username")
def command_demote(args):
    """Revoke a user's site admin status."""
    db: DbContext = args.get_db()
    user: Optional[User] = userq.try_from_username(db, args.username)
    if user is None:
        args.parser.error("User not found")
        return -1
    if not user.is_site_admin:
        LOG.info(f"{user.username} is not a site admin.")
    else:
        user.is_site_admin = False
        LOG.info(f"Revoking site admin status for {user.username}.")
        db.session.commit()
    return 0


def command_delete(args):
    """
    Delete a user.
    """
    raise NotImplementedError()


def command_list(args):
    """
    List all users.
    """
    raise NotImplementedError()


@add_argument("username")
@add_argument("password")
def command_passwd(args) -> int:
    """
    Set a user's password.
    """
    db: DbContext = args.get_db()
    userq.password_set(db, args.username, args.password)
    LOG.info(f"Updated password for {args.username}")
    return 0
