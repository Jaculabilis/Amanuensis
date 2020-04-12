def normalize_title(title):
	"""
	Normalizes strings as titles:
	- Strips leading and trailing whitespace
	- Merges internal whitespace into a single space
	- Capitalizes the first word
	"""
	cleaned = re.sub(r'\s+', " ", title.strip())
	return cleaned[0:1].upper() + cleaned[1:]

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