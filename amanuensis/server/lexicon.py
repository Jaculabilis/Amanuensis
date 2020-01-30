import json

from flask import Blueprint, render_template, url_for, redirect, g, flash
from flask_login import login_required, current_user

from amanuensis.config import json_ro, open_ex
from amanuensis.config.loader import ReadOnlyOrderedDict
from amanuensis.lexicon.manage import valid_add, add_player
from amanuensis.server.forms import LexiconConfigForm, LexiconJoinForm
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

	@bp.route('/session/settings/', methods=['GET', 'POST'])
	@lexicon_param
	@editor_required
	def settings(name):
		# Restrict to editor
		if not current_user.id == g.lexicon.editor:
			flash("Access is forbidden")
			return redirect(url_for('lexicon.session', name=name))

		form = LexiconConfigForm()

		# Load the config for the lexicon on load
		if not form.is_submitted():
			with json_ro(g.lexicon.config_path) as cfg:
				form.configText.data = json.dumps(cfg, indent=2)
			return render_template("lexicon/settings.html", form=form)

		if form.validate():
			# Check input is valid json
			try:
				cfg = json.loads(form.configText.data,
					object_pairs_hook=ReadOnlyOrderedDict)
			except json.decoder.JsonDecodeError:
				flash("Invalid JSON")
				return render_template("lexicon/settings.html", form=form)
			# Check input has all the required fields
			# TODO
			# Write the new config
			form.submit.submitted = False
			with open_ex(g.lexicon.config_path, mode='w') as f:
				json.dump(cfg, f, indent='\t')
				flash("Config updated")
			return redirect(url_for('lexicon.settings', name=name))

		return render_template("lexicon/settings.html", form=form)

	@bp.route('/statistics/', methods=['GET'])
	@lexicon_param
	@player_required_if_not_public
	def stats(name):
		return render_template('lexicon/statistics.html')

	return bp
