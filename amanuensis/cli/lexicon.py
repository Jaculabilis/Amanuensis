import logging

from .helpers import add_argument


COMMAND_NAME = "lexicon"
COMMAND_HELP = "Interact with lexicons."

LOG = logging.getLogger(__name__)


def command_create(args):
    """
    Create a lexicon.
    """
    raise NotImplementedError()


def command_delete(args):
    """
    Delete a lexicon.
    """
    raise NotImplementedError()


def command_list(args):
    """
    List all lexicons and their statuses.
    """
    raise NotImplementedError()
