# Standard library imports
from argparse import ArgumentParser
from functools import wraps
from json.decoder import JSONDecodeError


# These function wrappers allow us to use the same function for executing a
# command and for configuring it. This keeps command arg configuration close to
# where the command is defined and allows the main parser to use the same
# function to both set up and execute commands.

def add_argument(*args, **kwargs):
	"""Passes the given args and kwargs to subparser.add_argument"""

	def argument_adder(command):
		@wraps(command)
		def augmented_command(cmd_args):
			# Add this wrapper's command in the parser pass
			if isinstance(cmd_args, ArgumentParser):
				cmd_args.add_argument(*args, **kwargs)
				# If there are more command wrappers, pass through to them
				if command.__dict__.get('wrapper', False):
					command(cmd_args)
				# Parser pass doesn't return a value
				return None

			# Pass through transparently in the execute pass
			return command(cmd_args)

		# Mark the command as wrapped so control passes through
		augmented_command.__dict__['wrapper'] = True
		return augmented_command

	return argument_adder


def no_argument(command):
	"""Noops for subparsers"""
	@wraps(command)
	def augmented_command(cmd_args):
		# Noop in the parser pass
		if isinstance(cmd_args, ArgumentParser):
			return None
		# Pass through in the execute pass
		return command(cmd_args)

	return augmented_command


# Wrappers for commands requiring lexicon or username options

LEXICON_ARGS = ['--lexicon']
LEXICON_KWARGS = {
	'metavar': 'LEXICON',
	'dest': 'lexicon',
	'help': 'Specify a user to operate on'}
def requires_lexicon(command):
	@wraps(command)
	def augmented_command(cmd_args):
		# Add lexicon argument in parser pass
		if isinstance(cmd_args, ArgumentParser):
			cmd_args.add_argument(*LEXICON_ARGS, **LEXICON_KWARGS)
			# If there are more command wrappers, pass through to them
			if command.__dict__.get('wrapper', False):
				command(cmd_args)
			# Parser pass doesn't return a value
			return None

		# Verify lexicon argument in execute pass
		val = ((hasattr(cmd_args, 'lexicon')
			and getattr(cmd_args, 'lexicon'))
			or None)
		if not val:
			from amanuensis.config import logger
			logger.error("This command requires specifying a lexicon")
			return -1
		from amanuensis.lexicon import LexiconModel
		cmd_args.lexicon = LexiconModel.by(name=val) #TODO catch specific exceptions
		if cmd_args.lexicon is None:
			from amanuensis.config import logger
			logger.error('Could not find lexicon "{}"'.format(val))
			return -1
		return command(cmd_args)

	augmented_command.__dict__['wrapper'] = True
	return augmented_command

USER_ARGS = ['--user']
USER_KWARGS = {
	'metavar': 'USER',
	'dest': 'user',
	'help': 'Specify a user to operate on'}
def requires_user(command):
	"""
	Performs all necessary setup and verification for passing a user to a CLI
	command.
	"""
	@wraps(command)
	def augmented_command(cmd_args):
		# Add user argument in parser pass
		if isinstance(cmd_args, ArgumentParser):
			cmd_args.add_argument(*USER_ARGS, **USER_KWARGS)
			# If there are more command wrappers, pass through to them
			if command.__dict__.get('wrapper', False):
				command(cmd_args)
			# Parser pass doesn't return a value
			return None

		# Verify user argument in execute pass
		val = ((hasattr(cmd_args, "user")
			and getattr(cmd_args, "user"))
			or None)
		if not val:
			from amanuensis.config import logger
			logger.error("This command requires specifying a user")
			return -1
		from amanuensis.user import UserModel
		cmd_args.user = UserModel.by(name=val) #TODO catch specific exceptions
		if cmd_args.user is None:
			from amanuensis.config import logger
			logger.error('Could not find user "{}"'.format(val))
			return -1
		return command(cmd_args)

	augmented_command.__dict__['wrapper'] = True
	return augmented_command


# Wrapper for aliasing commands
def alias(cmd_alias):
	"""Adds an alias to the function dictionary"""
	def aliaser(command):
		aliases = command.__dict__.get('aliases', [])
		aliases.append(cmd_alias)
		command.__dict__['aliases'] = aliases
		return command
	return aliaser


# Helpers for common command tasks

CONFIG_GET_ROOT_VALUE = object()
def config_get(cfg, pathspec):
	"""
	Performs config --get for a given config

	cfg is from a with json_ro context
	path is the full pathspec, unsplit
	"""
	import json
	from amanuensis.config import logger

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
	return 0

def config_set(obj_id, cfg, set_tuple):
	"""
	Performs config --set for a given config

	config is from a "with json_rw" context
	set_tuple is a tuple of the pathspec and the value
	"""
	import json
	from amanuensis.config import logger
	pathspec, value = set_tuple
	if not pathspec:
		logger.error("Path must be non-empty")
	path = pathspec.split('.')
	try:
		value = json.loads(value)
	except JSONDecodeError:
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
	return 0
