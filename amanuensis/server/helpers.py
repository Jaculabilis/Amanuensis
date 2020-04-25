# Standard library imports
from datetime import datetime
from functools import wraps

# Third party imports
from flask import g, flash, redirect, url_for, current_app
from flask_login import current_user

# Module imports
from amanuensis.parser import filesafe_title
from amanuensis.models import ModelFactory, UserModel


def register_custom_filters(app):
	"""Adds custom filters to the Flask app"""

	@app.template_filter("user_attr")
	def get_user_attr(uid, attr):
		factory: ModelFactory = current_app.config['model_factory']
		user: UserModel = factory.user(uid)
		val = getattr(user.cfg, attr)
		return val

	@app.template_filter("asdate")
	def timestamp_to_readable(ts, formatstr="%Y-%m-%d %H:%M:%S"):
		if ts is None:
			return "null"
		dt = datetime.fromtimestamp(ts)
		return dt.strftime(formatstr)

	@app.template_filter("articlelink")
	def article_link(title):
		return url_for(
			'lexicon.article',
			name=g.lexicon.name,
			title=filesafe_title(title))


def lexicon_param(route):
	"""Wrapper for loading a route's lexicon"""
	@wraps(route)
	def with_lexicon(**kwargs):
		name = kwargs.get('name')
		model_factory: ModelFactory = current_app.config['model_factory']
		g.lexicon = model_factory.lexicon(name)
		if g.lexicon is None:
			flash(f'Couldn\'t find a lexicon with the name "{name}"')
			return redirect(url_for("home.home"))
		return route(**kwargs)
	return with_lexicon


def admin_required(route):
	"""
	Requires the user to be an admin to load this page
	"""
	@wraps(route)
	def admin_route(*args, **kwargs):
		if not current_user.cfg.is_admin:
			flash("You must be an admin to view this page")
			return redirect(url_for('home.home'))
		return route(*args, **kwargs)
	return admin_route


def player_required(route):
	"""
	Requires the user to be a player in the lexicon to load this page
	"""
	@wraps(route)
	def player_route(*args, **kwargs):
		if current_user.uid not in g.lexicon.cfg.join.joined:
			flash("You must be a player to view this page")
			return (redirect(url_for('lexicon.contents', name=g.lexicon.cfg.name))
				if g.lexicon.cfg.join.public
				else redirect(url_for('home.home')))
		return route(*args, **kwargs)
	return player_route


def player_required_if_not_public(route):
	"""
	Requires the user to be a player in the lexicon to load this page if the
	lexicon has join.public = false
	"""
	@wraps(route)
	def player_route(*args, **kwargs):
		if ((not g.lexicon.cfg.join.public)
				and current_user.uid not in g.lexicon.cfg.join.joined):
			flash("You must be a player to view this page")
			return redirect(url_for('home.home'))
		return route(*args, **kwargs)
	return player_route


def editor_required(route):
	"""
	Requires the user to be the editor of the current lexicon to load this
	page
	"""
	@wraps(route)
	def editor_route(*args, **kwargs):
		if current_user.uid != g.lexicon.cfg.editor:
			flash("You must be the editor to view this page")
			return redirect(url_for('lexicon.contents', name=g.lexicon.name))
		return route(*args, **kwargs)
	return editor_route
