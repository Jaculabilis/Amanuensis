from flask import (
	Blueprint,
	flash,
	redirect,
	url_for,
	g,
	render_template,
	Markup)
from flask_login import login_required, current_user

from amanuensis.lexicon import player_can_join_lexicon, add_player_to_lexicon
from amanuensis.parser import filesafe_title
from amanuensis.server.forms import LexiconJoinForm
from amanuensis.server.helpers import (
	lexicon_param,
	player_required_if_not_public)


bp_lexicon = Blueprint('lexicon', __name__,
	url_prefix='/lexicon/<name>',
	template_folder='.')


@bp_lexicon.route("/join/", methods=['GET', 'POST'])
@lexicon_param
@login_required
def join(name):
	if not g.lexicon.cfg.join.open:
		flash("This game isn't open for joining")
		return redirect(url_for('home.home'))

	form = LexiconJoinForm()

	if form.validate_on_submit():
		# Gate on password if one is required
		if (g.lexicon.cfg.join.password
				and form.password.data != g.lexicon.cfg.join.password):
			return redirect(url_for("lexicon.join", name=name))
		# Gate on join validity
		if player_can_join_lexicon(current_user, g.lexicon, form.password.data):
			add_player_to_lexicon(current_user, g.lexicon)
			return redirect(url_for("lexicon.contents", name=name)) # SESSION
		else:
			flash("Could not join game")
			return redirect(url_for("home.home", name=name))

	return render_template('lexicon.join.jinja', form=form)


@bp_lexicon.route('/contents/', methods=['GET'])
@lexicon_param
@player_required_if_not_public
def contents(name):
	articles = []
	filenames = g.lexicon.ctx.article.ls()
	for filename in filenames:
		with g.lexicon.ctx.article.read(filename) as a:
			articles.append({
				'title': a.title,
				'link': url_for('lexicon.article',
					name=name,
					title=filesafe_title(a.title)),
			})
	return render_template('lexicon.contents.jinja', articles=articles)


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
