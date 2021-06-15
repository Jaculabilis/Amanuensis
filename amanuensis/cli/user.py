import logging

from .helpers import add_argument


COMMAND_NAME = "user"
COMMAND_HELP = "Interact with users."

LOG = logging.getLogger(__name__)


def command_create(args):
    """
    Create a user.
    """
    raise NotImplementedError()


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


def command_passwd(args):
    """
    Set a user's password.
    """
    raise NotImplementedError()
