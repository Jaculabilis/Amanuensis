from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from amanuensis.config import json_ro, json_rw
from amanuensis.lexicon import LexiconModel
from amanuensis.lexicon.manage import create_lexicon, get_all_lexicons
from amanuensis.server.forms import LexiconCreateForm
from amanuensis.server.helpers import admin_required
from amanuensis.user import UserModel


def get_bp():
	"""Create a blueprint for pages outside of a specific lexicon"""
	bp = Blueprint('home', __name__, url_prefix='/home')

	@bp.route('/', methods=['GET'])
	def home():
		user_lexicons = []
		public_lexicons = []
		for lexicon in get_all_lexicons():
			if current_user.in_lexicon(lexicon):
				user_lexicons.append(lexicon)
			elif lexicon.join.public:
				public_lexicons.append(lexicon)
		return render_template(
			'home/home.html',
			user_lexicons=user_lexicons,
			public_lexicons=public_lexicons)

	@bp.route('/admin/', methods=['GET'])
	@login_required
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

	@bp.route("/admin/create/", methods=['GET', 'POST'])
	@login_required
	@admin_required
	def admin_create():
		form = LexiconCreateForm()

		if form.validate_on_submit():
			lexicon_name = form.lexiconName.data
			editor_name = form.editorName.data
			prompt = form.promptText.data
			editor = UserModel.by(name=editor_name)
			lexicon = create_lexicon(lexicon_name, editor)
			with json_rw(lexicon.config_path) as cfg:
				cfg.prompt = prompt
			return redirect(url_for('lexicon.session', name=lexicon_name))

		return render_template('home/create.html', form=form)

	return bp
