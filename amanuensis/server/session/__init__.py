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

from amanuensis.lexicon import (
	attempt_publish,
	get_player_characters,
	create_character_in_lexicon,
	get_draft)
from amanuensis.models import LexiconModel
from amanuensis.parser import parse_raw_markdown
from amanuensis.server.helpers import (
	lexicon_param,
	player_required,
	editor_required)

from .forms import (
	LexiconCharacterForm,
	LexiconReviewForm,
	LexiconPublishTurnForm,
	LexiconConfigForm)

from .editor import load_editor, new_draft, update_draft, PreviewHtmlRenderer


bp_session = Blueprint('session', __name__,
	url_prefix='/lexicon/<name>/session',
	template_folder='.')


@bp_session.route('/', methods=['GET', 'POST'])
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
	form = LexiconPublishTurnForm()
	if form.validate_on_submit():
		if attempt_publish(g.lexicon):
			return redirect(url_for('lexicon.contents', name=name))
		else:
			flash('Publish failed')
			return redirect(url_for('session.session', name=name))
	return render_template(
		'session.root.jinja',
		ready_articles=drafts,
		approved_articles=approved,
		characters=characters,
		publish_form=form)


@bp_session.route('/settings/', methods=['GET', 'POST'])
@lexicon_param
@editor_required
def settings(name):
	form: LexiconConfigForm = LexiconConfigForm(g.lexicon)

	if not form.is_submitted():
		# GET
		form.load(g.lexicon)
		return render_template('session.settings.jinja', form=form)

	if not form.validate():
		# POST with invalid data
		flash('Validation error')
		return render_template('session.settings.jinja', form=form)

	# POST with valid data
	form.save(g.lexicon)
	flash('Settings updated')
	return redirect(url_for('session.session', name=name))


@bp_session.route('/review/', methods=['GET', 'POST'])
@lexicon_param
@editor_required
def review(name):
	# Ensure the article exists
	draft = get_draft(g.lexicon, request.args.get('aid'))
	if not draft:
		flash("Unknown article id")
		return redirect(url_for('session.session', name=name))

	draft_filename = f'{draft.character}.{draft.aid}'
	with g.lexicon.ctx.draft.edit(draft_filename) as draft:
		# If the article was unreadied in the meantime, abort
		if not draft.status.ready:
			flash("Article was rescinded")
			return redirect(url_for('session.session', name=name))

		parsed_draft = parse_raw_markdown(draft.contents)
		preview = parsed_draft.render(PreviewHtmlRenderer(g.lexicon))
		rendered_html = preview.contents
		citations = preview.citations

		# If the article was already reviewed, just preview it
		if draft.status.approved:
			return render_template(
				"session.review.jinja",
				article_html=Markup(rendered_html),
				citations=citations)

		# Otherwise, prepare the review form
		form = LexiconReviewForm()
		if not form.validate_on_submit():
			# GET or POST with invalid data
			return render_template(
				"session.review.jinja",
				form=form,
				article_html=Markup(rendered_html),
				citations=citations)

		# POST with valid data
		if form.approved.data == LexiconReviewForm.REJECTED:
			draft.status.ready = False
			draft.status.approved = False
			g.lexicon.log(f"Article '{draft.title}' rejected ({draft.aid})")
			return redirect(url_for('session.session', name=name))
		else:
			draft.status.ready = True
			draft.status.approved = True
			g.lexicon.log(f"Article '{draft.title}' approved ({draft.aid})")

	# Draft was approved, check for asap publishing
	if g.lexicon.cfg.publish.asap:
		if attempt_publish(g.lexicon):
			redirect(url_for('lexicon.contents', name=name))
	return redirect(url_for('session.session', name=name))


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
