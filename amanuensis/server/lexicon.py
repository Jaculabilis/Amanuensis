import json

from flask import Blueprint, render_template, url_for, redirect, g, flash
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField

import config
from config.loader import ReadOnlyOrderedDict
import user
import lexicon


class LexiconConfigForm(FlaskForm):
	configText = TextAreaField("Config file")
	submit = SubmitField("Submit")


def get_bp():
	"""Create a blueprint for lexicon pages"""
	bp = Blueprint('lexicon', __name__, url_prefix='/lexicon/<name>')

	@bp.route('/contents/', methods=['GET'])
	@login_required
	def contents(name):
		lex = lexicon.LexiconModel.by(name=name)
		return render_template('lexicon/contents.html', lexicon=lex)

	@bp.route('/rules/', methods=['GET'])
	@login_required
	def rules(name):
		lex = lexicon.LexiconModel.by(name=name)
		return render_template('lexicon/rules.html', lexicon=lex)

	@bp.route('/session/', methods=['GET'])
	@login_required
	def session(name):
		lex = lexicon.LexiconModel.by(name=name)
		return render_template('lexicon/session.html', lexicon=lex)

	@bp.route('/session/edit/', methods=['GET', 'POST'])
	@login_required
	def session_edit(name):
		# Restrict to editor
		lex = lexicon.LexiconModel.by(name=name)
		if not current_user.id == lex.editor:
			flash("Access is forbidden")
			return redirect(url_for('lexicon.session', name=name))

		form = LexiconConfigForm()

		# Load the config for the lexicon on load
		if not form.is_submitted():
			with config.json_ro(lex.config_path) as cfg:
				form.configText.data = json.dumps(cfg, indent=2)
			return render_template("lexicon/session_edit.html", lexicon=lex, form=form)

		if form.validate():
			# Check input is valid json
			try:
				cfg = json.loads(form.configText.data, object_pairs_hook=ReadOnlyOrderedDict)
			except:
				flash("Invalid JSON")
				return render_template("lexicon/session_edit.html", lexicon=lex, form=form)
			# Check input has all the required fields
			# TODO
			# Write the new config
			with config.open_ex(lex.config_path, mode='w') as f:
				json.dump(cfg, f, indent='\t')
				flash("Config updated")

		return render_template("lexicon/session_edit.html", lexicon=lex, form=form)

	@bp.route('/statistics/', methods=['GET'])
	@login_required
	def stats(name):
		lex = lexicon.LexiconModel.by(name=name)
		return render_template('lexicon/statistics.html', lexicon=lex)

	return bp
