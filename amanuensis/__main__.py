# Standard library imports
import argparse

# Application imports
import cli
import configs


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
		dest="lexicon",
		help="The name of the lexicon to operate on")
	parser.add_argument("-v",
		action="store_true",
		dest="verbose",
		help="Enable debug logging")
	parser.set_defaults(func=lambda a: parser.print_help())
	subp = parser.add_subparsers(
		metavar="COMMAND",
		help="The command to execute")

	# Set up command subparsers.
	# command_ functions perform setup or execution depending on
	# whether their argument is an ArgumentParser.
	for name, func in valid_commands.items():
		# Create the subparser.
		cmd = subp.add_parser(name)
		# Delegate subparser setup.
		func(cmd)
		# Store function for later execution
		cmd.set_defaults(func=func)

	return parser

def no_command():
	print("nothing")

def main():
	# Enumerate valid commands from the CLI module.
	commands = {
		name[8:] : func
		for name, func in vars(cli).items()
		if name.startswith("command_")}

	args = get_parser(commands).parse_args()

	# Configure logging.
	if args.verbose:
		configs.log_verbose()

	# Execute command.
	args.func(args)

if __name__ == "__main__":
	import sys
	sys.exit(main())
