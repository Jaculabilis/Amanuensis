"""
Handler helper functions pertaining to the article editor
"""
import json
import uuid

from flask import (
	flash, redirect, url_for, render_template, Markup)
from flask_login import current_user

from amanuensis.lexicon import (
	get_player_characters,
	get_player_drafts,
	get_draft,
	title_constraint_analysis,
	content_constraint_analysis)
from amanuensis.models import LexiconModel
from amanuensis.parser import (
	normalize_title,
	parse_raw_markdown,
	PreviewHtmlRenderer)


def load_editor(lexicon: LexiconModel, aid: str):
	"""
	Load the editor page
	"""
	if aid:
		# Article specfied, load editor in edit mode
		article = get_draft(lexicon, aid)
		if not article:
			flash("Draft not found")
			return redirect(url_for('session.session', name=lexicon.cfg.name))
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
	# Check if the update is permitted
	aid = article_json.get('aid')
	article = get_draft(lexicon, aid)
	if not article:
		raise ValueError("missing article")
	if lexicon.cfg.character.get(article.character).player != current_user.uid:
		return ValueError("bad user")
	if article.status.approved:
		raise ValueError("bad status")

	# Perform the update
	title = article_json.get('title')
	contents = article_json.get('contents')
	status = article_json.get('status')

	parsed = parse_raw_markdown(contents)

	# HTML parsing
	preview = parsed.render(PreviewHtmlRenderer(lexicon))
	# Constraint analysis
	title_warnings, title_errors = title_constraint_analysis(
		lexicon, current_user, title)
	content_infos, content_warnings, content_errors = content_constraint_analysis(
		lexicon, current_user, article.character, parsed)
	if any(title_errors) or any(content_errors):
		status['ready'] = False

	# Article update
	filename = f'{article.character}.{aid}'
	with lexicon.ctx.draft.edit(filename) as draft:
		draft.title = normalize_title(title)
		draft.contents = contents
		draft.status.ready = status.get('ready', False)

	# Return canonical information to editor
	return {
		'title': draft.title,
		'status': {
			'ready': draft.status.ready,
			'approved': draft.status.approved,
		},
		'rendered': preview.contents,
		'citations': preview.citations,
		'info': content_infos,
		'warning': title_warnings + content_warnings,
		'error': title_errors + content_errors,
	}
