# Standard library imports
from argparse import ArgumentParser as AP


def add_argument(*args, **kwargs):
	def argument_adder(command):
		def augmented_command(cmd_args):
			if type(cmd_args) is AP:
				cmd_args.add_argument(*args, **kwargs)
			else:
				command(cmd_args)
		augmented_command.__doc__ = command.__doc__
		return augmented_command
	return argument_adder

@add_argument("--foo", action="store_true")
def command_a(args):
	"""a docstring"""
	print(args.foo)


