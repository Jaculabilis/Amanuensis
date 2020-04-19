import re
import urllib

def normalize_title(title):
	"""
	Normalizes strings as titles:
	- Strips leading and trailing whitespace
	- Merges internal whitespace into a single space
	- Capitalizes the first word
	"""
	cleaned = re.sub(r'\s+', " ", title.strip())
	return cleaned[:1].capitalize() + cleaned[1:]

def titlesort(title):
	"""
	Strips articles off of titles for alphabetical sorting purposes
	"""
	lower = title.lower()
	if lower.startswith("the "):
		return lower[4:]
	elif lower.startswith("an "):
		return lower[3:]
	elif lower.startswith("a "):
		return lower[2:]
	else:
		return lower

def filesafe_title(title):
	"""
	Makes an article title filename-safe.
	"""
	s = re.sub(r"\s+", '_', title)  # Replace whitespace with _
	s = re.sub(r"~", '-', s)        # parse.quote doesn't catch ~
	s = urllib.parse.quote(s)       # Encode all other characters
	s = re.sub(r"%", "", s)         # Strip encoding %s
	s = s[:64]                  	# Limit to 64 characters
	return s