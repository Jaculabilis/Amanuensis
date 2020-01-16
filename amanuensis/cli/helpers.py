# Standard library imports
from argparse import ArgumentParser as AP
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
			if type(cmd_args) is AP:
				cmd_args.add_argument(*args, **kwargs)
			if type(cmd_args) is not AP or second_layer:
				command(cmd_args)
		augmented_command.__dict__['wrapper'] = True
		return augmented_command
	return argument_adder

def no_argument(command):
	"""Noops for subparsers"""
	@wraps(command)
	def augmented_command(cmd_args):
		if type(cmd_args) is not AP:
			command(cmd_args)
	return augmented_command
