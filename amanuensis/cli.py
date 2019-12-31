# Standard library imports
from argparse import ArgumentParser as AP
from functools import wraps


def add_argument(*args, **kwargs):
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
	@wraps(command)
	def augmented_command(cmd_args):
		if type(cmd_args) is not AP:
			command(cmd_args)
	return augmented_command

@add_argument("--foo", action="store_true")
def command_a(args):
	"""a docstring"""
	print(args.foo)

