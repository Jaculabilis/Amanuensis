# Standard library imports
import json
import logging
import os

# Module imports
from amanuensis.errors import MissingConfigError, MalformedConfigError
import amanuensis.config.context
from amanuensis.config.context import is_guid
import amanuensis.config.init
import amanuensis.config.loader


# Environment variable name constants
ENV_SECRET_KEY = "AMANUENSIS_SECRET_KEY"
ENV_CONFIG_DIR = "AMANUENSIS_CONFIG_DIR"
ENV_LOG_FILE = "AMANUENSIS_LOG_FILE"
ENV_LOG_FILE_SIZE = "AMANUENSIS_LOG_FILE_SIZE"
ENV_LOG_FILE_NUM = "AMANUENSIS_LOG_FILE_NUM"

#
# The config directory can be set by cli input, so the config infrastructure
# needs to wait for initialization before it can load any configs.
#
CONFIG_DIR = None
GLOBAL_CONFIG = None
logger = None
root = None

def init_config(args):
	"""
	Initializes the config infrastructure to read configs from the
	directory given by args.config_dir. Initializes logging.
	"""
	global CONFIG_DIR, GLOBAL_CONFIG, logger, root
	CONFIG_DIR = args.config_dir
	amanuensis.config.init.verify_config_dir(CONFIG_DIR)
	with amanuensis.config.loader.json_ro(
			os.path.join(CONFIG_DIR, "config.json")) as cfg:
		GLOBAL_CONFIG = cfg
	amanuensis.config.init.init_logging(args, GLOBAL_CONFIG['logging'])
	logger = logging.getLogger("amanuensis")
	root = amanuensis.config.context.RootConfigDirectoryContext(CONFIG_DIR)

def get(key):
	return GLOBAL_CONFIG[key]

def prepend(*path):
	joined = os.path.join(*path)
	if not joined.startswith(CONFIG_DIR):
		joined = os.path.join(CONFIG_DIR, joined)
	return joined

def open_sh(*path, **kwargs):
	return amanuensis.config.loader.open_sh(prepend(*path), **kwargs)

def open_ex(*path, **kwargs):
	return amanuensis.config.loader.open_ex(prepend(*path), **kwargs)

def json_ro(*path, **kwargs):
	return amanuensis.config.loader.json_ro(prepend(*path), **kwargs)

def json_rw(*path, **kwargs):
	return amanuensis.config.loader.json_rw(prepend(*path), **kwargs)
