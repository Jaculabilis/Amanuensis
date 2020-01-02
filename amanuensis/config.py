# Standard library imports
from collections import OrderedDict as odict
import copy
import json
import logging
import logging.config
import os

# Module imports
from errors import MissingConfigError, MalformedConfigError


# Environment variable name constants
ENV_CONFIG_DIR =    "AMANUENSIS_CONFIG_DIR"
ENV_LOG_FILE =      "AMANUENSIS_LOG_FILE"
ENV_LOG_FILE_SIZE = "AMANUENSIS_LOG_FILE_SIZE"
ENV_LOG_FILE_NUM =  "AMANUENSIS_LOG_FILE_NUM"

# Functions to be used for moving configs on and off of disk.
def read(path):
	with open(path, 'r') as config_file:
		return json.load(config_file, object_pairs_hook=odict)

def write(config, path):
	with open(path, 'w') as dest_file:
		json.dump(config, dest_file, allow_nan=False, indent='\t')

#
# The config directory can be set by cli input, so the config infrastructure
# needs to wait for initialization before it can load any configs.
#
CONFIG_DIR = None
GLOBAL_CONFIG = None

def init(args):
	"""
	Initializes the config infrastructure to read configs from the
	directory given by args.config_dir. Initializes logging.
	"""
	# Check that config dir exists
	if not os.path.isdir(args.config_dir):
		raise MissingConfigError("Config directory not found: {}".format(args.config_dir))
	# Check that global config file exists
	global_config_path = os.path.join(args.config_dir, "config.json")
	if not os.path.isfile(global_config_path):
		raise MissingConfigError("Config directory missing global config file: {}".format(args.config_dir))
	# Check that global config file has logging settings
	global_config_file = read(global_config_path)
	if 'logging' not in global_config_file.keys():
		raise MalformedConfigError("No 'logging' section in global config")
	# Check that the global config file has a lexicon data directory
	if 'lexicon_data' not in global_config_file.keys():
		raise MalformedConfigError("No 'lexicon_data' setting in global config")
	# Configs verified, use them for initialization
	global CONFIG_DIR, GLOBAL_CONFIG
	CONFIG_DIR = args.config_dir
	GLOBAL_CONFIG = global_config_file
	# Initialize logging
	init_logging(args)

def init_logging(args):
	"""
	Initializes logging by using the logging section of the global config
	file.
	"""
	# Get the logging config section
	cfg = copy.deepcopy(GLOBAL_CONFIG['logging'])
	# Apply any commandline settings to what was defined in the config file
	handlers = cfg['loggers']['amanuensis']['handlers']
	if args.verbose:
		if 'cli-basic' in handlers:
			handlers.remove('cli_basic')
		handlers.append('cli_verbose')
	if args.log_file:
		cfg['handlers']['file']['filename'] = args.log_file
		handlers.append("file")
	# Load the config
	try:
		logging.config.dictConfig(cfg)
	except:
		raise MalformedConfigError("Failed to load logging config")

def logger():
	"""Returns the main logger"""
	return logging.getLogger("amanuensis")

# Global config values, which shouldn't be changing during runtime, are
# accessed through config.get()

def get(key):
	"""Gets the given config value from the global config"""
	return GLOBAL_CONFIG[key]

