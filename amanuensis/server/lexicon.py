import json
import uuid

from flask import (
	Blueprint, render_template, url_for, redirect, g, flash, request, Markup)
from flask_login import login_required, current_user

from amanuensis.config import root
from amanuensis.config.loader import ReadOnlyOrderedDict
from amanuensis.errors import MissingConfigError
from amanuensis.lexicon.manage import valid_add, add_player, add_character, attempt_publish
from amanuensis.parser import parse_raw_markdown, PreviewHtmlRenderer, FeatureCounter, filesafe_title
from amanuensis.server.forms import (
	LexiconConfigForm, LexiconJoinForm,LexiconCharacterForm, LexiconReviewForm)
from amanuensis.server.helpers import (
	lexicon_param, player_required, editor_required,
	player_required_if_not_public)


def jsonfmt(obj):
	return Markup(json.dumps(obj))


def get_bp():
	"""Create a blueprint for lexicon pages"""
	bp = Blueprint('lexicon', __name__, url_prefix='/lexicon/<name>')

	@bp.route("/join/", methods=['GET', 'POST'])
	@lexicon_param
	@login_required
	def join(name):
		if not g.lexicon.join.open:
			flash("This game isn't open for joining")
			return redirect(url_for('home.home'))

		form = LexiconJoinForm()

		if form.validate_on_submit():
			# Gate on password if one is required
			if (g.lexicon.join.password
					and form.password.data != g.lexicon.join.password):
				return redirect(url_for("lexicon.join", name=name))
			# Gate on join validity
			if valid_add(g.lexicon, current_user, form.password.data):
				add_player(g.lexicon, current_user)
				return redirect(url_for("lexicon.session", name=name))
			else:
				flash("Could not join game")
				return redirect(url_for("home.home", name=name))

		return render_template('lexicon/join.html', form=form)

	@bp.route('/contents/', methods=['GET'])
	@lexicon_param
	@player_required_if_not_public
	def contents(name):
		articles = []
		filenames = g.lexicon.ctx.article.ls()
		for filename in filenames:
			with g.lexicon.ctx.article.read(filename) as a:
				articles.append({
					'title': a.title,
					'link': url_for('lexicon.article', name=name, title=filesafe_title(a.title)),
				})
		return render_template('lexicon/contents.html', articles=articles)

	@bp.route('/article/<title>')
	@lexicon_param
	@player_required_if_not_public
	def article(name, title):
		with g.lexicon.ctx.article.read(title) as a:
			article = { **a, 'html': Markup(a['html']) }
			return render_template('lexicon/article.html', article=article)

	@bp.route('/rules/', methods=['GET'])
	@lexicon_param
	@player_required_if_not_public
	def rules(name):
		return render_template('lexicon/rules.html')

	@bp.route('/session/', methods=['GET'])
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
		return render_template(
			'lexicon/session.html',
			ready_articles=drafts,
			approved_articles=approved)

	def edit_character(name, form, cid):
		if form.validate_on_submit():
			# Update character
			form.update_character(g.lexicon, cid)
			flash('Character updated')
			return redirect(url_for('lexicon.session', name=name))

		if not form.is_submitted():
			# On GET, populate with the character
			form.for_character(g.lexicon, cid)
		return render_template('lexicon/character.html', form=form, action='edit')

	def create_character(name, form):
		if form.validate_on_submit():
			# On POST, verify character can be added
			if not g.lexicon.can_add_character(current_user.id):
				flash('Operation not permitted')
				return redirect(url_for('lexicon.session', name=name))
			# Add the character
			form.add_character(g.lexicon, current_user)
			flash('Character created')
			return redirect(url_for('lexicon.session', name=name))

		if not form.is_submitted():
			# On GET, populate form for new character
			form.for_new()
		return render_template('lexicon/character.html', form=form, action='create')

	@bp.route('/session/character/', methods=['GET', 'POST'])
	@lexicon_param
	@player_required
	def character(name):
		form = LexiconCharacterForm()
		cid = request.args.get('cid')
		if cid:
			if cid not in g.lexicon.character:
				flash('Character not found')
				return redirect(url_for('lexicon.session', name=name))
			if (g.lexicon.character.get(cid).player != current_user.id
					and g.lexicon.editor != current_user.id):
				flash('Access denied')
				return redirect(url_for('lexicon.session', name=name))
			return edit_character(name, form, cid)
		return create_character(name, form)

	@bp.route('/session/settings/', methods=['GET', 'POST'])
	@lexicon_param
	@editor_required
	def settings(name):
		form = LexiconConfigForm()
		form.set_options(g.lexicon)

		# Load the config for the lexicon on load
		if not form.is_submitted():
			form.populate_from_lexicon(g.lexicon)
			return render_template("lexicon/settings.html", form=form)

		if form.validate():
			if not form.update_lexicon(g.lexicon):
				flash("Error updating settings")
				return render_template("lexicon/settings.html", form=form)
			flash("Settings updated")
			return redirect(url_for('lexicon.session', name=name))

		flash("Validation error")
		return render_template("lexicon/settings.html", form=form)

	@bp.route('/session/review/', methods=['GET', 'POST'])
	@lexicon_param
	@editor_required
	def review(name):
		aid = request.args.get('aid')
		if not aid:
			flash("Unknown article id")
			return redirect(url_for('lexicon.session', name=name))

		draft_ctx = g.lexicon.ctx.draft
		draft_filename = [fn for fn in draft_ctx.ls() if aid in fn][0]
		with draft_ctx.edit(draft_filename) as draft:
			# If the article was unreadied in the meantime, abort
			if not draft.status.ready:
				flash("Article was rescinded")
				return redirect(url_for('lexicon.session', name=name))

			parsed_draft = parse_raw_markdown(draft.contents)
			rendered_html = parsed_draft.render(PreviewHtmlRenderer(g.lexicon))

			# If the article is ready and awaiting review
			if not draft.status.approved:
				form = LexiconReviewForm()
				if form.validate_on_submit():
					if form.approved.data == 'Y':
						draft.status.ready = True
						draft.status.approved = True
						g.lexicon.add_log(f"Article '{draft.title}' approved ({draft.aid})")
						if g.lexicon.publish.asap:
							attempt_publish(g.lexicon)
					else:
						draft.status.ready = False
						draft.status.approved = False
						g.lexicon.add_log(f"Article '{draft.title}' rejected ({draft.aid})")
					return redirect(url_for('lexicon.session', name=name))

			# If the article was already reviewed and this is just the preview
			else:
				form = None

		return render_template(
			"lexicon/review.html",
			form=form,
			article_html=Markup(rendered_html))

	@bp.route('/statistics/', methods=['GET'])
	@lexicon_param
	@player_required_if_not_public
	def stats(name):
		return render_template('lexicon/statistics.html')

	@bp.route('/session/editor/', methods=['GET'])
	@lexicon_param
	@player_required
	def editor(name):
		"""
		cases:
		- neither cid nor aid: load all chars and articles
		- cid: list articles just for cid
		- aid: 
		"""
		cid = request.args.get('cid')
		if not cid:
			# Character not specified, load all characters and articles
			# and return render_template
			characters = [
				char for char in g.lexicon.character.values()
				if char.player == current_user.id
			]
			articles = [
				article for article in g.lexicon.get_drafts_for_player(uid=current_user.id)
				if any([article.character == char.cid for char in characters])
			]
			return render_template(
				'lexicon/editor.html',
				characters=characters,
				articles=articles,
				jsonfmt=jsonfmt)

		character = g.lexicon.character.get(cid)
		if not character:
			# Character was specified, but id was invalid
			flash("Character not found")
			return redirect(url_for('lexicon.session', name=name))
		if character.player != current_user.id:
			# Player doesn't control this character
			flash("Access forbidden")
			return redirect(url_for('lexicon.session', name=name))

		aid = request.args.get('aid')
		if not aid:
			# Character specified but not article, load character articles
			# and retuen r_t
			articles = [
				article for article in g.lexicon.get_drafts_for_player(uid=current_user.id)
				if article.character == character.cid
			]
			return render_template(
				'lexicon/editor.html',
				character=character,
				articles=articles,
				jsonfmt=jsonfmt)

		filename = f'{cid}.{aid}'
		try:
			with g.lexicon.ctx.draft.read(filename) as a:
				article = a
		except MissingConfigError:
			flash("Draft not found")
			return redirect(url_for('lexicon.session', name=name))

		return render_template(
			'lexicon/editor.html',
			character=character,
			article=article,
			jsonfmt=jsonfmt)

	@bp.route('/session/editor/new', methods=['GET'])
	@lexicon_param
	@player_required
	def editor_new(name):
		new_aid = uuid.uuid4().hex
		# TODO harden this
		cid = request.args.get("cid")
		character = g.lexicon.character.get(cid)
		article = {
			"version": "0",
			"aid": new_aid,
			"lexicon": g.lexicon.id,
			"character": cid,
			"title": "",
			"turn": 1,
			"status": {
				"ready": False,
				"approved": False
			},
			"contents": f"\n\n{character.signature}",
		}
		filename = f"{cid}.{new_aid}"
		with g.lexicon.ctx.draft.new(filename) as j:
			j.update(article)
		return redirect(url_for('lexicon.editor', name=name, cid=cid, aid=new_aid))

	@bp.route('/session/editor/update', methods=['POST'])
	@lexicon_param
	@player_required
	def editor_update(name):
		article = request.json['article']
		# TODO verification
		# check if article was previously approved
		# check extrinsic constraints for blocking errors
		parsed_draft = parse_raw_markdown(article['contents'])
		rendered_html = parsed_draft.render(PreviewHtmlRenderer(g.lexicon))
		features = parsed_draft.render(FeatureCounter())

		filename = f'{article["character"]}.{article["aid"]}'
		with g.lexicon.ctx.draft.edit(filename) as a:
			a.update(article)

		# TODO return more info
		return {
			'article': article,
			'info': {
				'rendered': rendered_html,
				'word_count': features.word_count,
			}
		}

	return bp
