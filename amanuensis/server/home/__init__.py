from flask import Blueprint, render_template, g

import amanuensis.backend.user as userq
import amanuensis.backend.lexicon as lexiq

# from .forms import LexiconCreateForm

bp = Blueprint("home", __name__, url_prefix="/home", template_folder=".")


@bp.get("/")
def home():
    return render_template('home.root.jinja')


@bp.get("/admin/")
# @login_required
# @admin_required
def admin():
    return render_template("home.admin.jinja", userq=userq, lexiq=lexiq)


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
