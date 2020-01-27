# Standard library imports
import copy
import json
import logging.config
import os
import shutil

# Module imports
from amanuensis.errors import MissingConfigError, MalformedConfigError
from amanuensis.config.loader import json_ro, json_rw
from amanuensis.resources import get_stream


def create_config_dir(config_dir, refresh=False):
	"""
	Create or refresh a config directory
	"""
	from collections import OrderedDict
	import fcntl

	def prepend(*path):
		joined = os.path.join(*path)
		if not joined.startswith(config_dir):
			joined = os.path.join(config_dir, joined)
		return joined

	# Create the directory if it doesn't exist.
	if not os.path.isdir(config_dir):
		os.mkdir(config_dir)

	# The directory should be empty if we're not updating an existing one.
	if len(os.listdir(config_dir)) > 0 and not refresh:
		print("Directory {} is not empty".format(config_dir))
		return -1

	# Update or create global config.
	def_cfg = get_stream("global.json")
	global_config_path = prepend("config.json")
	if refresh and os.path.isfile(global_config_path):
		# We need to write an entirely different ordereddict to the config
		# file, so we mimic the config.loader functionality manually.
		with open(global_config_path, 'r+', encoding='utf8') as cfg_file:
			fcntl.lockf(cfg_file, fcntl.LOCK_EX)
			old_cfg = json.load(cfg_file, object_pairs_hook=OrderedDict)
			new_cfg = json.load(def_cfg, object_pairs_hook=OrderedDict)
			merged = {}
			for key in new_cfg:
				merged[key] = old_cfg[key] if key in old_cfg else new_cfg[key]
				if key not in old_cfg:
					print("Added key '{}' to config".format(key))
			for key in old_cfg:
				if key not in new_cfg:
					print("Config contains unknown key '{}'".format(key))
					merged[key] = old_cfg[key]
			cfg_file.seek(0)
			json.dump(merged, cfg_file, allow_nan=False, indent='\t')
			cfg_file.truncate()
			fcntl.lockf(cfg_file, fcntl.LOCK_UN)
	else:
		with open(prepend("config.json"), 'wb') as f:
			f.write(def_cfg.read())

	# Ensure pidfile exists.
	if not os.path.isfile(prepend("pid")):
		with open(prepend("pid"), 'w') as f:
			f.write(str(os.getpid()))

	# Ensure lexicon subdir exists.
	if not os.path.isdir(prepend("lexicon")):
		os.mkdir(prepend("lexicon"))
	if not os.path.isfile(prepend("lexicon", "index.json")):
		with open(prepend("lexicon", "index.json"), 'w') as f:
			json.dump({}, f)

	# Ensure user subdir exists.
	if not os.path.isdir(prepend("user")):
		os.mkdir(prepend("user"))
	if not os.path.isfile(prepend('user', 'index.json')):
		with open(prepend('user', 'index.json'), 'w') as f:
			json.dump({}, f)

	if refresh:
		for dir_name in ('lexicon', 'user'):
			# Clean up unindexed folders
			with json_ro(prepend(dir_name, 'index.json')) as index:
				known = list(index.values())
			entries = os.listdir(prepend(dir_name))
			for dir_entry in entries:
				if dir_entry == "index.json":
					continue
				if dir_entry in known:
					continue
				print("Removing unindexed folder: '{}/{}'"
					.format(dir_name, dir_entry))
				shutil.rmtree(prepend(dir_name, dir_entry))

			# Remove orphaned index listings
			with json_rw(prepend(dir_name, 'index.json')) as index:
				for name, entry in index.items():
					if not os.path.isdir(prepend(dir_name, entry)):
						print("Removing stale {} index entry '{}: {}'"
							.format(dir_name, name, entry))
						del index[name]


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
		raise MissingConfigError("Config directory missing global config file"
			": {}".format(config_dir))
	# Check that global config file has all the default settings
	def_cfg_s = get_stream("global.json")
	def_cfg = json.load(def_cfg_s)
	with json_ro(global_config_path) as global_config_file:
		for key in def_cfg.keys():
			if key not in global_config_file.keys():
				raise MalformedConfigError("Missing '{}' in global config. If"
					" you updated Amanuensis, run init --refresh to pick up n"
					"ew config keys".format(key))
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
