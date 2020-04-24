# Standard library imports
import argparse
import logging
import os
import sys

# Module imports
from amanuensis.cli import describe_commands, get_commands
from amanuensis.config import (
	RootConfigDirectoryContext,
	ENV_CONFIG_DIR,
	ENV_LOG_FILE)
from amanuensis.errors import AmanuensisError
from amanuensis.log import init_logging
from amanuensis.models import ModelFactory


def process_doc(docstring):
	return '\n'.join([
		line.strip()
		for line in (docstring or "").strip().splitlines()
	])


def get_parser(valid_commands):
	# Set up the top-level parser.
	parser = argparse.ArgumentParser(
		description=describe_commands(),
		formatter_class=argparse.RawDescriptionHelpFormatter)
	# The config directory.
	parser.add_argument("--config-dir",
		dest="config_dir",
		default=os.environ.get(ENV_CONFIG_DIR, "./config"),
		help="The config directory for Amanuensis")
	# Logging settings.
	parser.add_argument("--verbose", "-v",
		action="store_true",
		dest="verbose",
		help="Enable verbose console logging")
	parser.add_argument("--log-file",
		dest="log_file",
		default=os.environ.get(ENV_LOG_FILE),
		help="Enable verbose file logging")
	parser.set_defaults(func=lambda args: parser.print_help())
	subp = parser.add_subparsers(
		metavar="COMMAND",
		dest="command",
		help="The command to execute")

	# Set up command subparsers.
	# command_ functions perform setup or execution depending on
	# whether their argument is an ArgumentParser.
	for name, func in valid_commands.items():
		# Create the subparser, set the docstring as the description.
		cmd = subp.add_parser(name,
			description=process_doc(func.__doc__),
			formatter_class=argparse.RawDescriptionHelpFormatter,
			aliases=func.__dict__.get("aliases", []))
		# Delegate subparser setup to the command.
		func(cmd)
		# Store function for later execution.
		cmd.set_defaults(func=func)

	return parser


def main(argv):
	# Enumerate valid commands from the CLI module.
	commands = get_commands()

	# Parse args
	args = get_parser(commands).parse_args(argv)

	# First things first, initialize logging
	init_logging(args.verbose, args.log_file)
	logger = logging.getLogger('amanuensis')

	# The init command initializes a config directory at --config-dir.
	# All other commands assume that the config dir already exists.
	if args.command and args.command != "init":
		args.root = RootConfigDirectoryContext(args.config_dir)
		args.model_factory = ModelFactory(args.root)

	# If verbose logging, dump args namespace
	if args.verbose:
		logger.debug('amanuensis')
		for key, val in vars(args).items():
			logger.debug(f'  {key}: {val}')

	# Execute command.
	try:
		args.func(args)
	except AmanuensisError as e:
		logger.error('Unexpected internal {}: {}'.format(
			type(e).__name__, str(e)))


if __name__ == "__main__":
	sys.exit(main(sys.argv[1:]))
