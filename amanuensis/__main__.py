# Standard library imports
import argparse
import os
import traceback

# Module imports
import cli
import configs


def repl(args):
	"""Runs a REPL with the given lexicon"""
	# Get all the cli commands' descriptions and add help and exit.
	commands = {
		name[8:]: func.__doc__ for name, func in vars(cli).items()
		if name.startswith("command_")}
	commands['help'] = "Print this message"
	commands['exit'] = "Exit"
	print("Amanuensis running on Lexicon {}".format(args.lexicon))
	while True:
		# Read input in a loop.
		try:
			data = input("{}> ".format(args.lexicon))
		except EOFError:
			print()
			break
		tokens = data.strip().split()
		if not data.strip():
			pass
		elif tokens[0] not in commands:
			print("'{}' is not a valid command.".format(tokens[0]))
		elif data.strip() == "help":
			print("Available commands:")
			for name, func in commands.items():
				print("  {}: {}".format(name, func))
		elif data.strip() == "exit":
			print()
			break
		elif data.strip():
			# Execute the command by appending it to the argv the
			# REPL was invoked with.
			try:
				argv = sys.argv[1:] + data.split()
				main(argv)
			except Exception as e:
				traceback.print_exc()

def get_parser(valid_commands):
	# Pull out the command functions' docstrings to describe them.
	command_descs = "\n".join([
		"- {0}: {1}".format(name, func.__doc__)
		for name, func in valid_commands.items()])

	# Set up the top-level parser.
	parser = argparse.ArgumentParser(
		description="Available commands:\n{}\n".format(command_descs),
		formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument("-n",
		metavar="LEXICON",
		dest="lexicon",
		help="The name of the lexicon to operate on")
	parser.add_argument("-v",
		action="store_true",
		dest="verbose",
		help="Enable debug logging")
	parser.set_defaults(func=repl)
	subp = parser.add_subparsers(
		metavar="COMMAND",
		help="The command to execute")

	# Set up command subparsers.
	# command_ functions perform setup or execution depending on
	# whether their argument is an ArgumentParser.
	for name, func in valid_commands.items():
		# Create the subparser, set the docstring as the description.
		cmd = subp.add_parser(name, description=func.__doc__)
		# Delegate subparser setup to the command.
		func(cmd)
		# Store function for later execution.
		cmd.set_defaults(func=func)

	return parser

def main(argv):
	# Enumerate valid commands from the CLI module.
	commands = {
		name[8:] : func
		for name, func in vars(cli).items()
		if name.startswith("command_")}

	args = get_parser(commands).parse_args(argv)

	# Configure logging.
	if args.verbose:
		configs.log_verbose()

	# Execute command.
	args.func(args)

if __name__ == "__main__":
	import sys
	sys.exit(main(sys.argv[1:]))
