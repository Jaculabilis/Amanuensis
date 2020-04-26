"""
Handler helper functions pertaining to the article editor
"""
import json
import uuid

from flask import (
	flash, redirect, url_for, render_template, Markup)
from flask_login import current_user

from amanuensis.lexicon import get_player_characters, get_player_drafts
from amanuensis.models import LexiconModel
from amanuensis.parser import (
	parse_raw_markdown,
	PreviewHtmlRenderer,
	FeatureCounter)


def load_editor(lexicon: LexiconModel, aid: str):
	"""
	Load the editor page
	"""
	if aid:
		# Article specfied, load editor in edit mode
		article_fn = None
		for filename in lexicon.ctx.draft.ls():
			if filename.endswith(f'{aid}.json'):
				article_fn = filename
				break
		if not article_fn:
			flash("Draft not found")
			return redirect(url_for('session.session', name=lexicon.cfg.name))
		with lexicon.ctx.draft.read(article_fn) as a:
			article = a
		# Check that the player owns this article
		character = lexicon.cfg.character.get(article.character)
		if character.player != current_user.uid:
			flash("Access forbidden")
			return redirect(url_for('session.session', name=lexicon.cfg.name))
		return render_template(
			'session.editor.jinja',
			character=character,
			article=article,
			jsonfmt=lambda obj: Markup(json.dumps(obj)))

	# Article not specified, load editor in load mode
	characters = list(get_player_characters(lexicon, current_user.uid))
	articles = list(get_player_drafts(lexicon, current_user.uid))
	return render_template(
		'session.editor.jinja',
		characters=characters,
		articles=articles)


def new_draft(lexicon: LexiconModel, cid: str):
	"""
	Create a new draft and open it in the editor
	"""
	if cid:
		new_aid = uuid.uuid4().hex
		# TODO harden this
		character = lexicon.cfg.character.get(cid)
		article = {
			"version": "0",
			"aid": new_aid,
			"lexicon": lexicon.lid,
			"character": cid,
			"title": "",
			"turn": 1,
			"status": {
				"ready": False,
				"approved": False
			},
			"contents": f"\n\n{character.signature}",
		}
		filename = f"{cid}.{new_aid}"
		with lexicon.ctx.draft.new(filename) as j:
			j.update(article)
		return redirect(url_for(
			'session.editor',
			name=lexicon.cfg.name,
			cid=cid,
			aid=new_aid))

	# Character not specified
	flash('Character not found')
	return redirect(url_for('session.session', name=lexicon.cfg.name))


def update_draft(lexicon: LexiconModel, article_json):
	"""
	Update a draft and perform analysis on it
	"""
	aid = article_json.get('aid')
	# TODO check if article can be updated
	# article exists
	# player owns article
	# article is not already approved

	contents = article_json.get('contents')
	if contents is not None:
		parsed = parse_raw_markdown(contents)
		# HTML parsing
		rendered_html = parsed.render(PreviewHtmlRenderer(lexicon))
		# Constraint analysis
		# features = parsed_draft.render(FeatureCounter()) TODO
		filename = f'{article_json["character"]}.{article_json["aid"]}'
		with lexicon.ctx.draft.edit(filename) as article:
			# TODO
			article.contents = contents
		return {
			'article': article,
			'info': {
				'rendered': rendered_html,
				#'word_count': features.word_count,
			}
		}
	return {}
