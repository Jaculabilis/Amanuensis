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

	@bp.route('/session/', methods=['GET'])
	@login_required
	def session(name):
		return "Lexicon " + str(name)

	return bp
