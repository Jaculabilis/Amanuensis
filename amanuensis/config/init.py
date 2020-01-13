# Standard library imports
import copy
import json
import logging.config
import os
import pkg_resources

# Module imports
from errors import MissingConfigError, MalformedConfigError
from config.loader import json_ro


def verify_config_dir(config_dir):
	"""
	Verifies that the given directory has a valid global config in it and
	returns the global config if so
	"""
	# Check that config dir exists
	if not os.path.isdir(config_dir):
		raise MissingConfigError("Config directory not found: {}".format(config_dir))
	# Check that global config file exists
	global_config_path = os.path.join(config_dir, "config.json")
	if not os.path.isfile(global_config_path):
		raise MissingConfigError("Config directory missing global config file: {}".format(config_dir))
	# Check that global config file has all the default settings
	def_cfg_s = pkg_resources.resource_stream("__main__", "resources/default_config.json")
	def_cfg = json.load(def_cfg_s)
	with json_ro(global_config_path) as global_config_file:
		for key in def_cfg.keys():
			if key not in global_config_file.keys():
				raise MalformedConfigError("Missing '{}' in global config. If you updated Amanuensis, run init --update to pick up new config keys".format(key))
	# Configs verified
	return True

def init_logging(args, logging_config):
	"""
	Initializes logging by using the logging section of the global config
	file.
	"""
	# Get the logging config section
	cfg = copy.deepcopy(logging_config)
	# Apply any commandline settings to what was defined in the config file
	handlers = cfg['loggers']['amanuensis']['handlers']
	if args.verbose:
		if 'cli_basic' in handlers:
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

