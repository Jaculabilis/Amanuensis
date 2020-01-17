import os
import time
import uuid

import config
import lexicon
import resources

def create_lexicon(name, editor):
	"""
	"""
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