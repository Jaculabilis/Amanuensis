"""
Submodule of functions for creating and managing lexicons within the
general Amanuensis context.
"""
import json
import logging
import os
import re
import time
from typing import Iterable
import uuid

from amanuensis.config import RootConfigDirectoryContext, AttrOrderedDict
from amanuensis.errors import ArgumentError
from amanuensis.models import ModelFactory, UserModel, LexiconModel
from amanuensis.resources import get_stream

logger = logging.getLogger(__name__)


def valid_name(name: str) -> bool:
	"""
	Validates that a lexicon name consists only of alpahnumerics, dashes,
	underscores, and spaces
	"""
	return re.match(r'^[A-Za-z0-9-_ ]+$', name) is not None


def create_lexicon(
	root: RootConfigDirectoryContext,
	name: str,
	editor: UserModel) -> LexiconModel:
	"""
	Creates a lexicon with the given name and sets the given user as its editor
	"""
	# Verify arguments
	if not name:
		raise ArgumentError(f'Empty lexicon name: "{name}"')
	if not valid_name(name):
		raise ArgumentError(f'Invalid lexicon name: "{name}"')
	with root.lexicon.read_index() as extant_lexicons:
		if name in extant_lexicons.keys():
			raise ArgumentError(f'Lexicon name already taken: "{name}"')
	if editor is None:
		raise ArgumentError('Editor must not be None')

	# Create the lexicon directory and initialize it with a blank lexicon
	lid: str = uuid.uuid4().hex
	lex_dir = os.path.join(root.lexicon.path, lid)
	os.mkdir(lex_dir)
	with get_stream("lexicon.json") as s:
		path: str = os.path.join(lex_dir, 'config.json')
		with open(path, 'wb') as f:
			f.write(s.read())

	# Create subdirectories
	os.mkdir(os.path.join(lex_dir, 'draft'))
	os.mkdir(os.path.join(lex_dir, 'src'))
	os.mkdir(os.path.join(lex_dir, 'article'))

	# Update the index with the new lexicon
	with root.lexicon.edit_index() as index:
		index[name] = lid

	# Fill out the new lexicon
	with root.lexicon[lid].edit_config() as cfg:
		cfg.lid = lid
		cfg.name = name
		cfg.editor = editor.uid
		cfg.time.created = int(time.time())

	with root.lexicon[lid].edit('info', create=True):
		pass  # Create an empry config file

	# Load the lexicon and add the editor and default character
	model_factory: ModelFactory = ModelFactory(root)
	lexicon = model_factory.lexicon(lid)
	with lexicon.ctx.edit_config() as cfg:
		cfg.join.joined.append(editor.uid)
		with get_stream('character.json') as template:
			character = json.load(template, object_pairs_hook=AttrOrderedDict)
		character.cid = 'default'
		character.name = 'Ersatz Scrivener'
		character.player = None
		cfg.character.new(character.cid, character)

	# Log the creation
	message = f'Created {lexicon.title}, ed. {editor.cfg.displayname} ({lid})'
	lexicon.log(message)
	logger.info(message)

	return lexicon


def load_all_lexicons(
	root: RootConfigDirectoryContext) -> Iterable[LexiconModel]:
	"""
	Iterably loads every lexicon in the config store
	"""
	model_factory: ModelFactory = ModelFactory(root)
	with root.lexicon.read_index() as index:
		for lid in index.values():
			lexicon: LexiconModel = model_factory.lexicon(lid)
			yield lexicon
