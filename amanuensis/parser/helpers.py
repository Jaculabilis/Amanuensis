"""
Helper functions for manipulating titles during parsing
"""

import re
import urllib.parse


def normalize_title(title: str) -> str:
    """
    Normalizes strings as titles:
    - Strips leading and trailing whitespace
    - Merges internal whitespace into a single space
    - Capitalizes the first word
    """
    cleaned = re.sub(r"\s+", " ", title.strip())
    return cleaned[:1].capitalize() + cleaned[1:]


def titlesort(title: str) -> str:
    """
    Strips articles off of titles for alphabetical sorting purposes
    """
    lower = title.lower()
    if lower.startswith("the "):
        return lower[4:]
    if lower.startswith("an "):
        return lower[3:]
    if lower.startswith("a "):
        return lower[2:]
    return lower


def filesafe_title(title: str) -> str:
    """
    Makes an article title filename-safe.
    """
    # Replace whitespace with _
    s = re.sub(r"\s+", "_", title)

    # parse.quote doesn't catch ~
    s = re.sub(r"~", "-", s)

    # Encode all other characters
    s = urllib.parse.quote(s)

    # Strip encoding %s
    s = re.sub(r"%", "", s)

    # Limit to 64 characters
    s = s[:64]

    return s
