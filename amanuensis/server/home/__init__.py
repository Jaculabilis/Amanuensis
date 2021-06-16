from flask import Blueprint, render_template, g

# from flask import Blueprint, render_template, redirect, url_for, current_app
# from flask_login import login_required, current_user

import amanuensis.backend.user as userq
import amanuensis.backend.lexicon as lexiq

# from amanuensis.config import RootConfigDirectoryContext
# from amanuensis.lexicon import create_lexicon, load_all_lexicons
# from amanuensis.models import UserModel, ModelFactory
# from amanuensis.server.helpers import admin_required

# from .forms import LexiconCreateForm

bp = Blueprint("home", __name__, url_prefix="/home", template_folder=".")


# @bp.get("/")
# def home():
# Show lexicons that are visible to the current user
# return "TODO"
# user_lexicons = []
# public_lexicons = []
# for lexicon in load_all_lexicons(root):
# if user.uid in lexicon.cfg.join.joined:
#     user_lexicons.append(lexicon)
# elif lexicon.cfg.join.public:
# public_lexicons.append(lexicon)
# return render_template(
#     'home.root.jinja',
#     user_lexicons=user_lexicons,
#     public_lexicons=public_lexicons)


@bp.get("/admin/")
# @login_required
# @admin_required
def admin():
    return render_template("home.admin.jinja", db=g.db, userq=userq, lexiq=lexiq)


# @bp_home.route("/admin/create/", methods=['GET', 'POST'])
# @login_required
# @admin_required
# def admin_create():
#     form = LexiconCreateForm()

#     if not form.validate_on_submit():
#         # GET or POST with invalid form data
#         return render_template('home.create.jinja', form=form)

#     # POST with valid data
#     root: RootConfigDirectoryContext = current_app.config['root']
#     model_factory: ModelFactory = current_app.config['model_factory']
#     lexicon_name = form.lexiconName.data
#     editor_name = form.editorName.data
#     prompt = form.promptText.data
#     # Editor's existence was checked by form validators
#     editor = model_factory.user(editor_name)
#     lexicon = create_lexicon(root, lexicon_name, editor)
#     with lexicon.ctx.edit_config() as cfg:
#         cfg.prompt = prompt
#     return redirect(url_for('session.session', name=lexicon_name))
