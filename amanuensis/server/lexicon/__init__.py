from flask import (
	Blueprint,
	flash,
	redirect,
	url_for,
	g,
	render_template,
	Markup)
from flask_login import login_required, current_user

from amanuensis.lexicon import (
	player_can_join_lexicon,
	add_player_to_lexicon,
	sort_by_index_spec)
from amanuensis.models import LexiconModel
from amanuensis.server.helpers import (
	lexicon_param,
	player_required_if_not_public)

from .forms import LexiconJoinForm


bp_lexicon = Blueprint('lexicon', __name__,
	url_prefix='/lexicon/<name>',
	template_folder='.')


@bp_lexicon.route("/join/", methods=['GET', 'POST'])
@lexicon_param
@login_required
def join(name):
	if g.lexicon.status != LexiconModel.PREGAME:
		flash("Can't join a game already in progress")
		return redirect(url_for('home.home'))

	if not g.lexicon.cfg.join.open:
		flash("This game isn't open for joining")
		return redirect(url_for('home.home'))

	form = LexiconJoinForm()

	if not form.validate_on_submit():
		# GET or POST with invalid form data
		return render_template('lexicon.join.jinja', form=form)

	# POST with valid data
	# If the game is passworded, check password
	if (g.lexicon.cfg.join.password
		and form.password.data != g.lexicon.cfg.join.password):
		# Bad creds, try again
		flash('Incorrect password')
		return redirect(url_for('lexicon.join', name=name))
	# If the password was correct, check if the user can join
	if player_can_join_lexicon(current_user, g.lexicon, form.password.data):
		add_player_to_lexicon(current_user, g.lexicon)
		return redirect(url_for('session.session', name=name))
	else:
		flash('Could not join game')
		return redirect(url_for('home.home', name=name))


@bp_lexicon.route('/contents/', methods=['GET'])
@lexicon_param
@player_required_if_not_public
def contents(name):
	with g.lexicon.ctx.read('info') as info:
		indexed = sort_by_index_spec(info, g.lexicon.cfg.article.index.list)
		for articles in indexed.values():
			for i in range(len(articles)):
				articles[i] = {
					'title': articles[i],
					**info.get(articles[i])}
		return render_template('lexicon.contents.jinja', indexed=indexed)


@bp_lexicon.route('/article/<title>')
@lexicon_param
@player_required_if_not_public
def article(name, title):
	with g.lexicon.ctx.article.read(title) as a:
		article = {**a, 'html': Markup(a['html'])}
		return render_template('lexicon.article.jinja', article=article)


@bp_lexicon.route('/rules/', methods=['GET'])
@lexicon_param
@player_required_if_not_public
def rules(name):
	return render_template('lexicon.rules.jinja')


@bp_lexicon.route('/statistics/', methods=['GET'])
@lexicon_param
@player_required_if_not_public
def stats(name):
	return render_template('lexicon.statistics.jinja')
