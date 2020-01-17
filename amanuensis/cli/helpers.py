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

# This wrapper is another verification step

def requires(argument, verify=lambda a: a is not None):
	"""Errors out if the given argument is not present"""
	def req_checker(command):
		second_layer = command.__dict__.get('wrapper', False)
		@wraps(command)
		def augmented_command(cmd_args):
			if type(cmd_args) is Namespace:
				if not hasattr(cmd_args, argument) or not verify(getattr(cmd_args, argument)):
					import config
					config.logger.error(
						"This command requires specifying {}".format(argument))
					return -1
			command(cmd_args)
		augmented_command.__dict__['wrapper'] = True
		return augmented_command
	return req_checker

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

def config_set(cfg, set_tuple):
	"""
	Performs config --set for a given config

	config is from a with json_rw context
	set_tuple is a tuple of the pathspec and the value
	"""
	from config import logger
	pathspec, value = set_tuple
	if not pathspec:
		logger.error("Path must be non-empty")
	path = pathspec.split('.')
	if not value:
		value = None
	for spec in path[:-1]:
		if spec not in cfg:
			logger.error("Path not found")
			return -1
		cfg = cfg.get(spec)
	key = path[-1]
	if key not in cfg:
		logger.error("Path not found")
		return -1
	cfg[key] = value