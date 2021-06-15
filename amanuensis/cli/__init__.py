from argparse import ArgumentParser
import logging
import logging.config


LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "fmt_basic": {
            "validate": True,
            "format": "%(message)s",
        },
        "fmt_detailed": {
            "validate": True,
            "format": "%(asctime)s %(levelname)s %(message)s"
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
            "handlers": ["hnd_stderr"]
        }
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
    if (args.verbose):
        handler = LOGGING_CONFIG["handlers"]["hnd_stderr"]
        handler["formatter"] = "fmt_detailed"
        handler["level"] = "DEBUG"
    logging.config.dictConfig(LOGGING_CONFIG)


def main():
    """CLI entry point"""
    # Set up the top-level parser
    parser = ArgumentParser()
    parser.set_defaults(
        parser=parser,
        func=lambda args: parser.print_usage(),
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    # Add commands from cli submodules
    subparsers = parser.add_subparsers(metavar="COMMAND")

    # Parse args and execute the desired action
    args = parser.parse_args()
    init_logger(args)
    args.func(args)
