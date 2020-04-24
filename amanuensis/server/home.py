from flask import Blueprint, render_template, redirect, url_for, current_app
from flask_login import login_required, current_user

from amanuensis.config import RootConfigDirectoryContext
from amanuensis.lexicon import create_lexicon, load_all_lexicons
from amanuensis.models import UserModel
from amanuensis.server.forms import LexiconCreateForm
from amanuensis.server.helpers import admin_required
from amanuensis.user import load_all_users


bp_home = Blueprint('home', __name__, url_prefix='/home')


@bp_home.route('/', methods=['GET'])
def home():
	root: RootConfigDirectoryContext = current_app.config['root']
	user: UserModel = current_user
	user_lexicons = []
	public_lexicons = []
	for lexicon in load_all_lexicons(root):
		if user.uid in lexicon.cfg.join.joined:
			user_lexicons.append(lexicon)
		elif lexicon.cfg.join.public:
			public_lexicons.append(lexicon)
	return render_template(
		'home/home.jinja',
		user_lexicons=user_lexicons,
		public_lexicons=public_lexicons)


@bp_home.route('/admin/', methods=['GET'])
@login_required
@admin_required
def admin():
	root: RootConfigDirectoryContext = current_app.config['root']
	users = list(load_all_users(root))
	lexicons = list(load_all_lexicons(root))
	return render_template('home/admin.jinja', users=users, lexicons=lexicons)


@bp_home.route("/admin/create/", methods=['GET', 'POST'])
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
		with lexicon.ctx.edit_config() as cfg:
			cfg.prompt = prompt
		return redirect(url_for('lexicon.session', name=lexicon_name))

	return render_template('home/create.jinja', form=form)
