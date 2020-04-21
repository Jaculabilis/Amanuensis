import re
import urllib.parse


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
	s = re.sub(r"\s+", '_', title)  # Replace whitespace with _
	s = re.sub(r"~", '-', s)        # parse.quote doesn't catch ~
	s = urllib.parse.quote(s)       # Encode all other characters
	s = re.sub(r"%", "", s)         # Strip encoding %s
	s = s[:64]                  	# Limit to 64 characters
	return s
