# Standard library imports
from argparse import ArgumentParser, Namespace
from functools import wraps

# These function wrappers allow us to use the same function for executing a
# command and for configuring it. This keeps command arg configuration close to
# where the command is defined and allows the main parser to use the same
# function to both set up and execute commands.

def add_argument(*args, **kwargs):
	"""Passes the given args and kwargs to subparser.add_argument"""
	def argument_adder(command):
		second_layer = command.__dict__.get('wrapper', False)
		@wraps(command)
		def augmented_command(cmd_args):
			if type(cmd_args) is ArgumentParser:
				cmd_args.add_argument(*args, **kwargs)
			if type(cmd_args) is not ArgumentParser or second_layer:
				command(cmd_args)
		augmented_command.__dict__['wrapper'] = True
		return augmented_command
	return argument_adder

def no_argument(command):
	"""Noops for subparsers"""
	@wraps(command)
	def augmented_command(cmd_args):
		if type(cmd_args) is not ArgumentParser:
			command(cmd_args)
	return augmented_command

# Wrappers for commands requiring lexicon or username options

def requires_lexicon(command):
	@wraps(command)
	def augmented_command(cmd_args):
		if type(cmd_args) is ArgumentParser:
			cmd_args.add_argument("-n", metavar="LEXICON", dest="lexicon", help="Specify a lexicon to operate on")
			if command.__dict__.get('wrapper', False):
				command(cmd_args)
		if type(cmd_args) is Namespace:
			base_val = hasattr(cmd_args, "tl_lexicon") and getattr(cmd_args, "tl_lexicon")
			subp_val = hasattr(cmd_args, "lexicon") and getattr(cmd_args, "lexicon")
			val = subp_val or base_val or None
			if not val:
				import config
				config.logger.error("This command requires specifying a lexicon")
				return -1
			from lexicon import LexiconModel
			cmd_args.lexicon = val#LexiconModel.by(name=val).name
			command(cmd_args)
	augmented_command.__dict__['wrapper'] = True
	return augmented_command

def requires_username(command):
	@wraps(command)
	def augmented_command(cmd_args):
		if type(cmd_args) is ArgumentParser:
			cmd_args.add_argument("-u", metavar="USERNAME", dest="username", help="Specify a user to operate on")
			if command.__dict__.get('wrapper', False):
				command(cmd_args)
		if type(cmd_args) is Namespace:
			base_val = hasattr(cmd_args, "tl_username") and getattr(cmd_args, "tl_lexicon")
			subp_val = hasattr(cmd_args, "username") and getattr(cmd_args, "username")
			val = subp_val or base_val or None
			if not val:
				import config
				config.logger.error("This command requires specifying a user")
				return -1
			from user import UserModel
			cmd_args.username = val#UserModel.by(name=val).name
			command(cmd_args)
	augmented_command.__dict__['wrapper'] = True
	return augmented_command

# Helpers for common command tasks

CONFIG_GET_ROOT_VALUE = object()
def config_get(cfg, pathspec):
	"""
	Performs config --get for a given config

	cfg is from a with json_ro context
	path is the full pathspec, unsplit
	"""
	import json
	from config import logger

	if pathspec is CONFIG_GET_ROOT_VALUE:
		path = []
	else:
		path = pathspec.split(".")
	for spec in path:
		if spec not in cfg:
			logger.error("Path not found: {}".format(pathspec))
			return -1
		cfg = cfg.get(spec)
	print(json.dumps(cfg, indent=2))

def config_set(obj_id, cfg, set_tuple):
	"""
	Performs config --set for a given config

	config is from a "with json_rw" context
	set_tuple is a tuple of the pathspec and the value
	"""
	import json
	from config import logger
	pathspec, value = set_tuple
	if not pathspec:
		logger.error("Path must be non-empty")
	path = pathspec.split('.')
	try:
		value = json.loads(value)
	except:
		pass # Leave value as string
	for spec in path[:-1]:
		if spec not in cfg:
			logger.error("Path not found")
			return -1
		cfg = cfg.get(spec)
	key = path[-1]
	if key not in cfg:
		logger.error("Path not found")
		return -1
	old_value = cfg[key]
	cfg[key] = value
	logger.info("{}.{}: {} -> {}".format(obj_id, pathspec, old_value, value))