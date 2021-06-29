"""
Submodule of custom exception types
"""


class AmanuensisError(Exception):
    """Base class for exceptions in Amanuensis"""


class ArgumentError(AmanuensisError):
    """An internal call was made with invalid arguments."""


class BackendArgumentTypeError(ArgumentError):
    """
    A call to a backend function was made with a value of an invalid type for the parameter.
    Specify the invalid parameter and value as a kwarg.
    """

    def __init__(self, obj_type, **kwarg):
        if not kwarg:
            raise ValueError("Missing kwarg")
        param, value = next(iter(kwarg.items()))
        msg = f"Expected {param} of type {obj_type}, got {type(value)}"
        super().__init__(msg)
