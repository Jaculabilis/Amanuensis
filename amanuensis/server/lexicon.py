from functools import wraps
import json

from flask import Blueprint, render_template, url_for, redirect, g, flash
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField

from amanuensis.config import json_ro, open_ex
from amanuensis.config.loader import ReadOnlyOrderedDict
from amanuensis.lexicon import LexiconModel
from amanuensis.user import UserModel


def lexicon_param(route):
	@wraps(route)
	def with_lexicon(name):
		g.lexicon = LexiconModel.by(name=name)
		if g.lexicon is None:
			flash("Couldn't find a lexicon with the name '{}'".format(name))
			return redirect(url_for("home.home"))
		return route(name)
	return with_lexicon


class LexiconConfigForm(FlaskForm):
	configText = TextAreaField("Config file")
	submit = SubmitField("Submit")


def get_bp():
	"""Create a blueprint for lexicon pages"""
	bp = Blueprint('lexicon', __name__, url_prefix='/lexicon/<name>')

	@bp.route('/contents/', methods=['GET'])
	@login_required
	@lexicon_param
	def contents(name):
		return render_template('lexicon/contents.html')

	@bp.route('/rules/', methods=['GET'])
	@login_required
	@lexicon_param
	def rules(name):
		return render_template('lexicon/rules.html')

	@bp.route('/session/', methods=['GET'])
	@login_required
	@lexicon_param
	def session(name):
		return render_template('lexicon/session.html')

	@bp.route('/session/settings/', methods=['GET', 'POST'])
	@login_required
	@lexicon_param
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
				cfg = json.loads(form.configText.data, object_pairs_hook=ReadOnlyOrderedDict)
			except:
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
	@login_required
	@lexicon_param
	def stats(name):
		return render_template('lexicon/statistics.html')

	return bp
