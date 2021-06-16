import collections
import json
import logging
import os

from amanuensis.db import DbContext

from .helpers import add_argument


COMMAND_NAME = "admin"
COMMAND_HELP = "Interact with Amanuensis."

LOG = logging.getLogger(__name__)


@add_argument("--drop", "-d", action="store_true", help="Overwrite existing database")
def command_init_db(args) -> int:
    """
    Initialize the Amanuensis database.
    """
    if args.drop:
        open(args.db_path, mode="w").close()

    # Initialize the database
    LOG.info(f"Creating database at {args.db_path}")
    args.get_db().create_all()

    LOG.info("Done")
    return 0


@add_argument("path", metavar="CONFIG_PATH", help="Path to the config file")
def command_secret_key(args) -> int:
    """
    Generate a Flask secret key.

    The Flask server will not run unless a secret key has
    been generated.
    """
    # Load the json config
    with open(args.path, mode="r", encoding="utf8") as f:
        config = json.load(f, object_pairs_hook=collections.OrderedDict)

    # Set the secret key to a new random string
    config["SECRET_KEY"] = os.urandom(32).hex()

    # Write the config back out
    with open(args.path, mode="w", encoding="utf8") as f:
        json.dump(config, f, indent=2)

    LOG.info("Regenerated Flask secret key")
    return 0
