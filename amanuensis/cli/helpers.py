"""
Helpers for cli commands.
"""


def add_argument(*args, **kwargs):
    """Defines an argument to a cli command."""

    def argument_adder(command_func):
        """Decorator function for storing parser args on the function."""

        # Store the kw/args in the function dictionary
        add_args = command_func.__dict__.get("add_argument", [])
        add_args.append((args, kwargs))
        command_func.__dict__["add_argument"] = add_args

        # Return the same function
        return command_func

    return argument_adder
