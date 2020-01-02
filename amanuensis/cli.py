# Standard library imports
from argparse import ArgumentParser as AP
from functools import wraps

#
# The cli module must not import other parts of the application at the module
# level. This is because most other modules depend on the config module. The
# config module may depend on __main__'s commandline parsing to locate config
# files, and __main__'s commandline parsing requires importing (but not
# executing) the functions in the cli module. Thus, cli functions must only
# import the config module inside the various command methods, which are only
# run after commandline parsing has already occurred.
#

#
# These function wrappers are used to make the command_* methods accept an
# ArgumentParser as a parameter, which it then configures with the given
# argument and returns. This way, we can configure each command's subparser
# in this module without having to write a separate function to configure it.
#
def add_argument(*args, **kwargs):
	"""Passes the given args and kwargs to subparser.add_argument"""
	def argument_adder(command):
		@wraps(command)
		def augmented_command(cmd_args):
			if type(cmd_args) is AP:
				cmd_args.add_argument(*args, **kwargs)
			else:
				command(cmd_args)
		return augmented_command
	return argument_adder

def no_argument(command):
	"""Noops for subparsers"""
	@wraps(command)
	def augmented_command(cmd_args):
		if type(cmd_args) is not AP:
			command(cmd_args)
	return augmented_command

@add_argument("--foo", action="store_true")
def command_dump(args):
	"""Dumps the global config or the config for the given lexicon"""
	import json
	import configs
	print(json.dumps(configs.GLOBAL_CONFIG, indent=2))

