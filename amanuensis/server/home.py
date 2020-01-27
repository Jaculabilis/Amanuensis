from flask import Blueprint, render_template
from flask_login import login_required

from amanuensis.config import json_ro
from amanuensis.lexicon import LexiconModel
from amanuensis.server.forms import LexiconCreateForm
from amanuensis.server.helpers import admin_required
from amanuensis.user import UserModel


def get_bp():
	"""Create a blueprint for pages outside of a specific lexicon"""
	bp = Blueprint('home', __name__, url_prefix='/home')

	@bp.route('/', methods=['GET'])
	def home():
		return render_template('home/home.html')

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
			return "<br>".join([lexicon_name, editor_name, prompt])

		return render_template('home/create.html', form=form)

	return bp
