from functools import wraps
import json

from flask import Blueprint, render_template, url_for, redirect
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField

import config
import user
import lexicon

class AdminDashboardForm(FlaskForm):
	lexiconName = StringField("Lexicon name")
	configText = TextAreaField("Config file")
	submit = SubmitField("Submit")

def admin_required(route):
	"""Requires the user to be an admin"""
	@wraps(route)
	def admin_route(*args, **kwargs):
		if not current_user.is_admin:
			return redirect(url_for('home.home'))
		return route(*args, **kwargs)
	return admin_route

def get_bp():
	"""Create a blueprint for pages outside of a specific lexicon"""
	bp = Blueprint('home', __name__, url_prefix='/home')

	@bp.route('/', methods=['GET'])
	@login_required
	def home():
		return render_template('home/home.html')

	@bp.route('/admin/', methods=['GET', 'POST'])
	@admin_required
	def admin():
		form = AdminDashboardForm()
		if not form.is_submitted():
			return render_template('home/admin.html', form=form)

		if form.lexiconName.data:
			lid = None
			with config.json_ro('lexicon', 'index.json') as index:
				lid = index.get(form.lexiconName.data)
			if lid is not None:
				with config.json_ro('lexicon', lid, 'config.json') as cfg:
					form.configText.data = json.dumps(cfg, indent=2)
					form.lexiconName.data = ""
		elif form.configText.data:
			return "Update config"
		else:
			pass
		return render_template('home/admin.html', form=form)

	return bp
