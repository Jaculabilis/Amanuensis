"""
Submodule of custom exception types
"""

class AmanuensisError(Exception):
    """Base class for exceptions in amanuensis"""


class ArgumentError(AmanuensisError):
    """An internal call was made with invalid arguments"""
