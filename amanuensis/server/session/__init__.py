import uuid

from flask import (
	Blueprint,
	render_template,
	url_for,
	redirect,
	g,
	flash,
	request,
	Markup)
from flask_login import current_user

from amanuensis.lexicon import attempt_publish
from amanuensis.models import LexiconModel
from amanuensis.parser import (
	parse_raw_markdown,
	PreviewHtmlRenderer,
	FeatureCounter)
from amanuensis.server.forms import (
	LexiconConfigForm,
	LexiconCharacterForm,
	LexiconReviewForm)
from amanuensis.server.helpers import (
	lexicon_param,
	player_required,
	editor_required)

from .editor import load_editor, new_draft, update_draft


bp_session = Blueprint('session', __name__,
	url_prefix='/lexicon/<name>/session',
	template_folder='.')


@bp_session.route('/', methods=['GET'])
@lexicon_param
@player_required
def session(name):
	drafts = []
	approved = []
	draft_ctx = g.lexicon.ctx.draft
	draft_filenames = draft_ctx.ls()
	for draft_filename in draft_filenames:
		with draft_ctx.read(draft_filename) as draft:
			if draft.status.ready and not draft.status.approved:
				drafts.append(draft)
			if draft.status.approved:
				approved.append(draft)
	characters = []
	for char in g.lexicon.cfg.character.values():
		if char.player == current_user.uid:
			characters.append(char)
	return render_template(
		'session.root.jinja',
		ready_articles=drafts,
		approved_articles=approved,
		characters=characters)


def edit_character(name, form, cid):
	if form.validate_on_submit():
		# Update character
		form.update_character(g.lexicon, cid)
		flash('Character updated')
		return redirect(url_for('session.session', name=name))

	if not form.is_submitted():
		# On GET, populate with the character
		form.for_character(g.lexicon, cid)
	return render_template('session.character.jinja', form=form, action='edit')


def create_character(name, form):
	if form.validate_on_submit():
		# On POST, verify character can be added
		if not g.lexicon.can_add_character(current_user.uid):
			flash('Operation not permitted')
			return redirect(url_for('session.session', name=name))
		# Add the character
		form.add_character(g.lexicon, current_user)
		flash('Character created')
		return redirect(url_for('session.session', name=name))

	if not form.is_submitted():
		# On GET, populate form for new character
		form.for_new()
	return render_template('session.character.jinja', form=form, action='create')


@bp_session.route('/character/', methods=['GET', 'POST'])
@lexicon_param
@player_required
def character(name):
	form = LexiconCharacterForm()
	cid = request.args.get('cid')
	if cid:
		if cid not in g.lexicon.cfg.character:
			flash('Character not found')
			return redirect(url_for('session.session', name=name))
		if (g.lexicon.cfg.character.get(cid).player != current_user.uid
				and g.lexicon.cfg.editor != current_user.uid):
			flash('Access denied')
			return redirect(url_for('session.session', name=name))
		return edit_character(name, form, cid)
	return create_character(name, form)


@bp_session.route('/settings/', methods=['GET', 'POST'])
@lexicon_param
@editor_required
def settings(name):
	form = LexiconConfigForm()
	form.set_options(g.lexicon)

	# Load the config for the lexicon on load
	if not form.is_submitted():
		form.populate_from_lexicon(g.lexicon)
		return render_template('session.settings.jinja', form=form)

	if form.validate():
		if not form.update_lexicon(g.lexicon):
			flash("Error updating settings")
			return render_template("lexicon.settings.jinja", form=form)
		flash("Settings updated")
		return redirect(url_for('session.session', name=name))

	flash("Validation error")
	return render_template('session.settings.jinja', form=form)


@bp_session.route('/review/', methods=['GET', 'POST'])
@lexicon_param
@editor_required
def review(name):
	aid = request.args.get('aid')
	if not aid:
		flash("Unknown article id")
		return redirect(url_for('session.session', name=name))

	draft_ctx = g.lexicon.ctx.draft
	draft_filename = [fn for fn in draft_ctx.ls() if aid in fn][0]
	with draft_ctx.edit(draft_filename) as draft:
		# If the article was unreadied in the meantime, abort
		if not draft.status.ready:
			flash("Article was rescinded")
			return redirect(url_for('session.session', name=name))

		parsed_draft = parse_raw_markdown(draft.contents)
		rendered_html = parsed_draft.render(PreviewHtmlRenderer(g.lexicon))

		# If the article is ready and awaiting review
		if not draft.status.approved:
			form = LexiconReviewForm()
			if form.validate_on_submit():
				if form.approved.data == 'Y':
					draft.status.ready = True
					draft.status.approved = True
					g.lexicon.log(f"Article '{draft.title}' approved ({draft.aid})")
					if g.lexicon.cfg.publish.asap:
						attempt_publish(g.lexicon)
				else:
					draft.status.ready = False
					draft.status.approved = False
					g.lexicon.log(f"Article '{draft.title}' rejected ({draft.aid})")
				return redirect(url_for('session.session', name=name))

		# If the article was already reviewed and this is just the preview
		else:
			form = None

	return render_template(
		"session.review.jinja",
		form=form,
		article_html=Markup(rendered_html))


@bp_session.route('/editor/', methods=['GET'])
@lexicon_param
@player_required
def editor(name):
	lexicon: LexiconModel = g.lexicon
	aid: str = request.args.get('aid')
	return load_editor(lexicon, aid)


@bp_session.route('/editor/new', methods=['GET'])
@lexicon_param
@player_required
def editor_new(name):
	lexicon: LexiconModel = g.lexicon
	cid: str = request.args.get('cid')
	return new_draft(lexicon, cid)


@bp_session.route('/editor/update', methods=['POST'])
@lexicon_param
@player_required
def editor_update(name):
	lexicon: LexiconModel = g.lexicon
	article_json = request.json['article']
	return update_draft(lexicon, article_json)
	# only need to be sending around title, status, contents, aid
