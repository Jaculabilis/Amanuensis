import json

from flask import (
	Blueprint, render_template, url_for, redirect, g, flash, request)
from flask_login import login_required, current_user

from amanuensis.config import json_ro, open_ex
from amanuensis.config.loader import ReadOnlyOrderedDict
from amanuensis.lexicon.manage import valid_add, add_player, add_character
from amanuensis.server.forms import (
	LexiconConfigForm, LexiconJoinForm,LexiconCharacterForm)
from amanuensis.server.helpers import (
	lexicon_param, player_required, editor_required,
	player_required_if_not_public)


def get_bp():
	"""Create a blueprint for lexicon pages"""
	bp = Blueprint('lexicon', __name__, url_prefix='/lexicon/<name>')

	@bp.route("/join/", methods=['GET', 'POST'])
	@lexicon_param
	@login_required
	def join(name):
		if not g.lexicon.join.open:
			flash("This game isn't open for joining")
			return redirect(url_for('home.home'))

		form = LexiconJoinForm()

		if form.validate_on_submit():
			# Gate on password if one is required
			if (g.lexicon.join.password
					and form.password.data != g.lexicon.join.password):
				flash("Incorrect password")
				print("redirecting")
				return redirect(url_for("lexicon.join", name=name))
			# Gate on join validity
			if valid_add(g.lexicon, current_user, form.password.data):
				add_player(g.lexicon, current_user)
				return redirect(url_for("lexicon.session", name=name))
			else:
				flash("Could not join game")
				return redirect(url_for("lexicon.join", name=name))

		return render_template('lexicon/join.html', form=form)

	@bp.route('/contents/', methods=['GET'])
	@lexicon_param
	@player_required_if_not_public
	def contents(name):
		return render_template('lexicon/contents.html')

	@bp.route('/rules/', methods=['GET'])
	@lexicon_param
	@player_required_if_not_public
	def rules(name):
		return render_template('lexicon/rules.html')

	@bp.route('/session/', methods=['GET'])
	@lexicon_param
	@player_required
	def session(name):
		return render_template('lexicon/session.html')

	def edit_character(name, form, cid):
		if form.validate_on_submit():
			# Update character
			form.update_character(g.lexicon, cid)
			flash('Character updated')
			return redirect(url_for('lexicon.session', name=name))

		if not form.is_submitted():
			# On GET, populate with the character
			form.for_character(g.lexicon, cid)
		return render_template('lexicon/character.html', form=form, action='edit')

	def create_character(name, form):
		if form.validate_on_submit():
			# On POST, verify character can be added
			if not g.lexicon.can_add_character(current_user.id):
				flash('Operation not permitted')
				return redirect(url_for('lexicon.session', name=name))
			# Add the character
			form.add_character(g.lexicon, current_user)
			flash('Character created')
			return redirect(url_for('lexicon.session', name=name))

		if not form.is_submitted():
			# On GET, populate form for new character
			form.for_new()
		return render_template('lexicon/character.html', form=form, action='create')

	@bp.route('/session/character/', methods=['GET', 'POST'])
	@lexicon_param
	@player_required
	def character(name):
		form = LexiconCharacterForm()
		cid = request.args.get('cid')
		if cid:
			if cid not in g.lexicon.character:
				flash('Character not found')
				return redirect(url_for('lexicon.session', name=name))
			if g.lexicon.character.get(cid).player != current_user.id:
				flash('Access denied')
				return redirect(url_for('lexicon.session', name=name))
			return edit_character(name, form, cid)
		return create_character(name, form)

	@bp.route('/session/settings/', methods=['GET', 'POST'])
	@lexicon_param
	@editor_required
	def settings(name):
		form = LexiconConfigForm()
		form.set_options(g.lexicon)

		# Load the config for the lexicon on load
		if not form.is_submitted():
			form.populate_from_lexicon(g.lexicon)
			return render_template("lexicon/settings.html", form=form)

		if form.validate():
			if not form.update_lexicon(g.lexicon):
				flash("Error updating settings")
				return render_template("lexicon/settings.html", form=form)
			flash("Settings updated")
			return redirect(url_for('lexicon.session', name=name))

		flash("Validation error")
		return render_template("lexicon/settings.html", form=form)

	@bp.route('/statistics/', methods=['GET'])
	@lexicon_param
	@player_required_if_not_public
	def stats(name):
		return render_template('lexicon/statistics.html')

	return bp
