import json

from flask import Blueprint, render_template, url_for, redirect
from flask_login import login_required, current_user
# from flask_wtf import FlaskForm
# from wtforms import TextAreaField, SubmitField, StringField

import config
import user
import lexicon


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

	@bp.route('/statistics/', methods=['GET'])
	@login_required
	def stats(name):
		lex = lexicon.LexiconModel.by(name=name)
		return render_template('lexicon/statistics.html', lexicon=lex)

	return bp