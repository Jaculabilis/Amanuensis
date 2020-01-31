# Standard library imports
from datetime import datetime
from functools import wraps

# Third party imports
from flask import g, flash, redirect, url_for
from flask_login import current_user

# Module imports
from amanuensis.lexicon import LexiconModel
from amanuensis.user import UserModel


def register_custom_filters(app):
	"""Adds custom filters to the Flask app"""

	@app.template_filter("user_attr")
	def get_user_attr(uid, attr):
		user = UserModel.by(uid=uid)
		val = getattr(user, attr)
		return val

	@app.template_filter("asdate")
	def timestamp_to_readable(ts, formatstr="%Y-%m-%d %H:%M:%S"):
		if ts is None:
			return "null"
		dt = datetime.fromtimestamp(ts)
		return dt.strftime(formatstr)


def lexicon_param(route):
	"""Wrapper for loading a route's lexicon"""
	@wraps(route)
	def with_lexicon(name):
		g.lexicon = LexiconModel.by(name=name)
		if g.lexicon is None:
			flash("Couldn't find a lexicon with the name '{}'".format(name))
			return redirect(url_for("home.home"))
		return route(name)
	return with_lexicon


def admin_required(route):
	"""
	Requires the user to be an admin to load this page
	"""
	@wraps(route)
	def admin_route(*args, **kwargs):
		if not current_user.is_admin:
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
		if not current_user.in_lexicon(g.lexicon):
			flash("You must be a player to view this page")
			return (redirect(url_for('lexicon.contents', name=g.lexicon.name))
				if g.lexicon.join.public
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
		if ((not g.lexicon.join.public)
				and not current_user.in_lexicon(g.lexicon)):
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
		if current_user.id != g.lexicon.editor:
			flash("You must be the editor to view this page")
			return redirect(url_for('lexicon.contents', name=g.lexicon.name))
		return route(*args, **kwargs)
	return editor_route