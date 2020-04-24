"""
Functions for managing lexicons, primarily within the context of the
Amanuensis config directory.
"""
import json
import os
import re
import shutil
import time
import uuid

from amanuensis.config import prepend, json_rw, json_ro, logger
from amanuensis.config.loader import AttrOrderedDict
from amanuensis.errors import ArgumentError
from amanuensis.lexicon import LexiconModel
from amanuensis.parser import parse_raw_markdown, GetCitations, HtmlRenderer, filesafe_title, titlesort
from amanuensis.resources import get_stream





def delete_lexicon(lex, purge=False):
	"""
	Deletes the given lexicon from the internal configuration

	Does not delete the lexicon from the data folder unless purge=True.
	"""
	# Verify arguments
	if lex is None:
		raise ArgumentError("Invalid lexicon: '{}'".format(lex))

	# Delete the lexicon from the index
	with json_rw('lexicon', 'index.json') as index:
		if lex.name in index:
			del index[lex.name]

	# Delete the lexicon data folder if purging
	if purge:
		raise NotImplementedError()

	# Delete the lexicon config
	lex_path = prepend('lexicon', lex.id)
	shutil.rmtree(lex_path)


def get_all_lexicons():
	"""
	Loads each lexicon in the lexicon index
	"""
	# Get all the lexicon ids in the index
	with json_ro('lexicon', 'index.json') as index:
		lids = list(index.values())

	# Load all of the lexicons
	lexes = list(map(lambda id: LexiconModel.by(lid=id), lids))

	return lexes


def get_user_lexicons(user):
	"""
	Loads each lexicon that the given user is a player in
	"""
	return [
		lexicon
		for lexicon in get_all_lexicons()
		if user.in_lexicon(lexicon)]


def remove_player(lex, player):
	"""
	Remove a player from a lexicon
	"""
	# Verify arguments
	if lex is None:
		raise ArgumentError("Invalid lexicon: '{}'".format(lex))
	if player is None:
		raise ArgumentError("Invalid player: '{}'".format(player))
	if lex.editor == player.id:
		raise ArgumentError(
			"Can't remove the editor '{}' from lexicon '{}'".format(
				player.username, lex.name))

	# Idempotently remove player
	with json_rw(lex.config_path) as cfg:
		if player.id in cfg.join.joined:
			cfg.join.joined.remove(player.id)

	# TODO Reassign the player's characters to the editor


def add_character(lex, player, charinfo={}):
	"""
	Unconditionally adds a character to a lexicon

	charinfo is a dictionary of character settings
	"""
	# Verify arguments
	if lex is None:
		raise ArgumentError("Invalid lexicon: '{}'".format(lex))
	if player is None:
		raise ArgumentError("Invalid player: '{}'".format(player))
	if not charinfo or not charinfo.get("name"):
		raise ArgumentError("Invalid character info: '{}'".format(charinfo))
	charname = charinfo.get("name")
	if any([
			char.name for char in lex.character.values()
			if char.name == charname]):
		raise ArgumentError("Duplicate character name: '{}'".format(charinfo))

	# Load the character template
	with get_stream('character.json') as template:
		character = json.load(template, object_pairs_hook=AttrOrderedDict)

	# Fill out the character's information
	character.cid = charinfo.get("cid") or uuid.uuid4().hex
	character.name = charname
	character.player = charinfo.get("player") or player.id
	character.signature = charinfo.get("signature") or ("~" + character.name)

	# Add the character to the lexicon
	added = False
	with json_rw(lex.config_path) as cfg:
		cfg.character.new(character.cid, character)
		added = True

	# Log addition
	if added:
			lex.add_log("Character '{0.name}' created ({0.cid})".format(character))

def delete_character(lex, charname):
	"""
	Delete a character from a lexicon
	"""
	# Verify arguments
	if lex is None:
		raise ArgumentError("Invalid lexicon: '{}'".format(lex))
	if charname is None:
		raise ArgumentError("Invalid character name: '{}'".format(charname))

	# Find character in this lexicon
	matches = [
		char for cid, char in lex.character.items()
		if char.name == charname]
	if len(matches) != 1:
		raise ArgumentError(matches)
	char = matches[0]

	# Remove character from character list
	with json_rw(lex.config_path) as cfg:
		del cfg.character[char.cid]


def attempt_publish(lexicon):
	# Need to do checks

	# Get the articles to publish
	draft_ctx = lexicon.ctx.draft
	drafts = draft_ctx.ls()
	turn = []
	for draft_fn in drafts:
		with draft_ctx.read(draft_fn) as draft:
			if draft.status.approved:
				draft_fn = f'{draft.character}.{draft.aid}'
				turn.append(draft_fn)

	return publish_turn(lexicon, turn)

def publish_turn(lexicon, drafts):
	# Move the drafts to src
	draft_ctx = lexicon.ctx.draft
	src_ctx =  lexicon.ctx.src
	for filename in drafts:
		with draft_ctx.read(filename) as source:
			with src_ctx.edit(filename, create=True) as dest:
				dest.update(source)
		draft_ctx.delete(filename)

	# Load all articles in the source directory and rebuild their renderable trees
	article_model_by_title = {}
	article_renderable_by_title = {}
	for filename in src_ctx.ls():
		with src_ctx.read(filename) as article:
			article_model_by_title[article.title] = article
			article_renderable_by_title[article.title] = parse_raw_markdown(article.contents)

	# Get all citations
	citations_by_title = {}
	for title, article in article_renderable_by_title.items():
		citations_by_title[title] = sorted(set(article.render(GetCitations())), key=titlesort)

	# Get the written and phantom lists from the citation map
	written_titles = list(citations_by_title.keys())
	phantom_titles = []
	for citations in citations_by_title.values():
		for title in citations:
			if title not in written_titles and title not in phantom_titles:
				phantom_titles.append(title)

	# Build the citation map and save it to the info cache
	# TODO delete obsolete entries?
	with lexicon.ctx.edit('info', create=True) as info:
		for title in written_titles:
			info[title] = {
				'citations': citations_by_title[title],
				'character': article_model_by_title[title].character
			}
		for title in phantom_titles:
			info[title] = {
				'citations': [],
				'character': None,
			}

	# Render article HTML and save to article cache
	rendered_html_by_title = {}
	for title, article in article_renderable_by_title.items():
		html = article.render(HtmlRenderer(lexicon.name, written_titles))
		filename = filesafe_title(title)
		with lexicon.ctx.article.edit(filename, create=True) as f:
			f['title'] = title
			f['html'] = html
			f['cites'] = citations_by_title[title]
			f['citedby'] = [
				citer for citer, citations
				in citations_by_title.items()
				if title in citations]

	for title in phantom_titles:
		filename = filesafe_title(title)
		with lexicon.ctx.article.edit(filename, create=True) as f:
			f['title'] = title
			f['html'] = ""
			f['cites'] = []
			f['citedby'] = [
				citer for citer, citations
				in citations_by_title.items()
				if title in citations]
