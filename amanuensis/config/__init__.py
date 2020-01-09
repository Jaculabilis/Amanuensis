# Standard library imports
import json
import logging
import os

# Module imports
from errors import MissingConfigError, MalformedConfigError
import config.init
import config.loader


# Environment variable name constants
ENV_SECRET_KEY =    "AMANUENSIS_SECRET_KEY"
ENV_CONFIG_DIR =    "AMANUENSIS_CONFIG_DIR"
ENV_LOG_FILE =      "AMANUENSIS_LOG_FILE"
ENV_LOG_FILE_SIZE = "AMANUENSIS_LOG_FILE_SIZE"
ENV_LOG_FILE_NUM =  "AMANUENSIS_LOG_FILE_NUM"

#
# The config directory can be set by cli input, so the config infrastructure
# needs to wait for initialization before it can load any configs.
#
CONFIG_DIR = None
GLOBAL_CONFIG = None
logger = None

def init_config(args):
	"""
	Initializes the config infrastructure to read configs from the
	directory given by args.config_dir. Initializes logging.
	"""
	global CONFIG_DIR, GLOBAL_CONFIG, logger
	CONFIG_DIR = args.config_dir
	config.init.verify_config_dir(CONFIG_DIR)
	with config.loader.json_ro(os.path.join(CONFIG_DIR, "config.json")) as cfg:
		GLOBAL_CONFIG = cfg
	config.init.init_logging(args, GLOBAL_CONFIG['logging'])
	logger = logging.getLogger("amanuensis")

def get(key):
	return GLOBAL_CONFIG[key]

def prepend(*path):
	return os.path.join(CONFIG_DIR, *path)

def open_sh(path, mode):
	return config.loader.open_sh(prepend(path), mode)

def open_ex(path, mode):
	return config.loader.open_ex(prepend(path), mode)

def json_ro(*path):
	return config.loader.json_ro(prepend(*path))

def json_rw(*path):
	return config.loader.json_rw(prepend(*path))

def new_user(user_json):
	user_dir = prepend("user", user_json['uid'])
	# Create user dir and put config in it
	os.mkdir(user_dir)
	with config.loader.open_ex(os.path.join(user_dir, "config.json"), 'w') as f:
		json.dump(user_json, f, allow_nan=False, indent='\t')
	# Ensure index exists
	if not os.path.isdir(prepend('user', 'index.json')):
		with open_ex(prepend('user', 'index.json'), 'w') as f:
			json.dump({}, f)
	# Update index
	with json_rw('user', 'index.json') as j:
		j[user_json['username']] = user_json['uid']
