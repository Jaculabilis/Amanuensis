"""
Functions for managing lexicons, primarily within the context of the
Amanuensis config directory.
"""
import os
import re
import shutil
import time
import uuid

import config
import lexicon
import resources

def valid_name(name):
	"""
	Validates that a lexicon name consists only of alpahnumerics, dashes,
	underscores, and spaces
	"""
	return name is not None and re.match(r"^[A-Za-z0-9-_ ]+$", name) is not None


def create_lexicon(name, editor):
	"""
	Creates a lexicon with the given name and sets the given user as its editor
	"""
	# Verify arguments
	if not valid_name(name):
		raise ValueError("Invalid lexicon name: '{}'".format(name))
	if editor is None:
		raise ValueError("Invalid editor: '{}'".format(editor))

	# Create the lexicon directory and initialize it with a blank lexicon
	lid = uuid.uuid4().hex
	lex_dir = config.prepend("lexicon", lid)
	os.mkdir(lex_dir)
	with resources.get_stream("lexicon.json") as s:
		with open(config.prepend(lex_dir, 'config.json'), 'wb') as f:
			f.write(s.read())

	# Fill out the new lexicon
	with config.json_rw(lex_dir, 'config.json') as cfg:
		cfg['lid'] = lid
		cfg['name'] = name
		cfg['editor'] = editor.uid
		cfg['time']['created'] = int(time.time())

	# Update the index with the new lexicon
	with config.json_rw('lexicon', 'index.json') as index:
		index[name] = lid

	# Load the Lexicon and log creation
	l = lexicon.LexiconModel(lid)
	l.log("Lexicon created")

	config.logger.info("Created Lexicon {0.name}, ed. {1.displayname} ({0.id})".format(
		l, editor))

	return l


def delete_lexicon(lex, purge=False):
	"""
	Deletes the given lexicon from the internal configuration

	Does not delete the lexicon from the data folder unless purge=True.
	"""
	# Verify arguments
	if lex is None:
		raise ValueError("Invalid lexicon: '{}'".format(lex))
	
	# Delete the lexicon from the index
	with config.json_rw('lexicon', 'index.json') as j:
		if lex.id in j:
			del j[lex.id]

	# Delete the lexicon data folder if purging
	if purge:
		raise NotImplementedError()

	# Delete the lexicon config
	lex_path = config.prepend('lexicon', lex.id)
	shutil.rmtree(lex_path)


def get_all_lexicons():
	"""
	Loads each lexicon in the lexicon index
	"""
	# Get all the lexicon ids in the index
	with config.json_ro('lexicon', 'index.json') as index:
		lids = list(index.values())

	# Load all of the lexicons
	lexes = map(lambda id: lexicon.LexiconModel.by(lid=id), lids)

	return lexes