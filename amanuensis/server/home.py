from functools import wraps
import json

from flask import Blueprint, render_template, url_for, redirect, flash
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField

from amanuensis.config import json_ro
from amanuensis.lexicon import LexiconModel
from amanuensis.server.helpers import admin_required
from amanuensis.user import UserModel


def get_bp():
	"""Create a blueprint for pages outside of a specific lexicon"""
	bp = Blueprint('home', __name__, url_prefix='/home')

	@bp.route('/', methods=['GET'])
	def home():
		return render_template('home/home.html')

	@bp.route('/admin/', methods=['GET', 'POST'])
	@admin_required
	def admin():
		users = []
		with json_ro('user', 'index.json') as index:
			for name, uid in index.items():
				users.append(UserModel.by(uid=uid))

		lexicons = []
		with json_ro('lexicon', 'index.json') as index:
			for name, lid in index.items():
				lexicons.append(LexiconModel.by(lid=lid))

		return render_template('home/admin.html', users=users, lexicons=lexicons)

	return bp
