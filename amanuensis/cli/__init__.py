from argparse import ArgumentParser, Namespace
import logging
import logging.config
import os
from typing import Callable

import amanuensis.cli.admin
import amanuensis.cli.lexicon
import amanuensis.cli.user
from amanuensis.db import DbContext


LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "fmt_basic": {
            "validate": True,
            "format": "%(message)s",
        },
        "fmt_detailed": {
            "validate": True,
            "format": "%(asctime)s %(levelname)s %(message)s",
        },
    },
    "handlers": {
        "hnd_stderr": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "fmt_basic",
        },
    },
    "loggers": {
        __name__: {
            "level": "DEBUG",
            "handlers": ["hnd_stderr"],
        },
    },
}


def add_subcommand(subparsers, module) -> None:
    """Add a cli submodule's commands as a subparser."""
    # Get the command information from the module
    command_name: str = getattr(module, "COMMAND_NAME")
    command_help: str = getattr(module, "COMMAND_HELP")
    if not command_name and command_help:
        return

    # Add the subparser for the command and set a default action
    command_parser: ArgumentParser = subparsers.add_parser(
        command_name, help=command_help
    )
    command_parser.set_defaults(func=lambda args: command_parser.print_usage())

    # Add all subcommands in the command module
    subcommands = command_parser.add_subparsers(metavar="SUBCOMMAND")
    for name, obj in vars(module).items():
        if name.startswith("command_"):
            # Hyphenate subcommand names
            sc_name: str = name[8:].replace("_", "-")
            # Only the first line of the subcommand function docstring is used
            sc_help = ((obj.__doc__ or "").strip() or "\n").splitlines()[0]

            # Add the command and any arguments defined by its decorators
            subcommand: ArgumentParser = subcommands.add_parser(
                sc_name, help=sc_help, description=obj.__doc__
            )
            subcommand.set_defaults(func=obj)
            for args, kwargs in obj.__dict__.get("add_argument", []):
                subcommand.add_argument(*args, **kwargs)


def init_logger(args):
    """Set up logging based on verbosity args"""
    if args.verbose:
        handler = LOGGING_CONFIG["handlers"]["hnd_stderr"]
        handler["formatter"] = "fmt_detailed"
        handler["level"] = "DEBUG"
    logging.config.dictConfig(LOGGING_CONFIG)


def get_db_factory(parser: ArgumentParser, args: Namespace) -> Callable[[], DbContext]:
    """Factory function for lazy-loading the database in subcommands."""

    def get_db() -> DbContext:
        """Lazy loader for the database connection."""
        if not os.path.exists(args.db_path):
            parser.error(f"No database found at {args.db_path}")
        return DbContext(path=args.db_path, echo=args.verbose)

    return get_db


def main():
    """CLI entry point"""
    # Set up the top-level parser
    parser = ArgumentParser()
    parser.set_defaults(
        parser=parser,
        func=lambda args: parser.print_usage(),
        get_db=None,
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--db", dest="db_path", default="db.sqlite", help="Path to Amanuensis database"
    )

    # Add commands from cli submodules
    subparsers = parser.add_subparsers(metavar="COMMAND")
    add_subcommand(subparsers, amanuensis.cli.admin)
    add_subcommand(subparsers, amanuensis.cli.lexicon)
    add_subcommand(subparsers, amanuensis.cli.user)

    # Parse args and perform top-level arg processing
    args = parser.parse_args()
    init_logger(args)
    args.get_db = get_db_factory(parser, args)

    # Execute the desired action
    args.func(args)
