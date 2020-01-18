from functools import wraps

from flask import Blueprint, render_template, url_for, redirect
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField

import config
import user

class DashboardForm(FlaskForm):
	admin_config_text = TextAreaField()
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

	@bp.route('/admin/', methods=['GET'])
	@admin_required
	def admin():
		with config.json_ro('config.json') as j:
			global_config = j
		import json
		text = json.dumps(j, indent=2, allow_nan=False)

		form = DashboardForm()
		if form.is_submitted():
			return "k"
		else:
			form.admin_config_text.data = text
			return render_template('home/admin.html', form=form)

	return bp
