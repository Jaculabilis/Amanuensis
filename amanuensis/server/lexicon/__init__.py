from flask import Blueprint, flash, redirect, url_for, g, render_template, Markup
from flask_login import login_required, current_user

from amanuensis.backend import lexiq, memq
from amanuensis.db import DbContext, Lexicon, User
from amanuensis.errors import ArgumentError
from amanuensis.server.helpers import lexicon_param, player_required_if_not_public

from .characters import bp as characters_bp
from .forms import LexiconJoinForm


bp = Blueprint(
    "lexicon", __name__, url_prefix="/lexicon/<lexicon_name>", template_folder="."
)
bp.register_blueprint(characters_bp)


@bp.route("/join/", methods=["GET", "POST"])
@lexicon_param
@login_required
def join(lexicon_name):
    lexicon: Lexicon = g.lexicon
    if not lexicon.joinable:
        flash("This game isn't open for joining")
        return redirect(url_for("home.home"))

    form = LexiconJoinForm()

    if not form.validate_on_submit():
        # GET or POST with invalid form data
        return render_template(
            "lexicon.join.jinja", lexicon_name=lexicon_name, form=form
        )

    # POST with valid data
    # If the game is passworded, check password
    db: DbContext = g.db
    if lexicon.join_password and not lexiq.password_check(
        db, lexicon.id, form.password.data
    ):
        # Bad creds, try again
        flash("Incorrect password")
        return redirect(url_for("lexicon.join", lexicon_name=lexicon_name))

    # If the password was correct, check if the user can join
    user: User = current_user
    try:
        memq.create(db, user.id, lexicon.id, is_editor=False)
        return redirect(url_for("session.session", lexicon_name=lexicon_name))
    except ArgumentError:
        flash("Could not join game")
        return redirect(url_for("home.home", lexicon_name=lexicon_name))


@bp.get("/contents/")
@lexicon_param
@player_required_if_not_public
def contents(lexicon_name):
    # indexed = sort_by_index_spec(info, g.lexicon.cfg.article.index.list)
    # for articles in indexed.values():
    #     for i in range(len(articles)):
    #         articles[i] = {
    #             'title': articles[i],
    #             **info.get(articles[i])}
    return render_template("lexicon.contents.jinja", lexicon_name=lexicon_name)


@bp.get("/article/<title>")
@lexicon_param
@player_required_if_not_public
def article(lexicon_name, title):
    # article = {**a, 'html': Markup(a['html'])}
    return render_template("lexicon.article.jinja", lexicon_name=lexicon_name)


@bp.get("/rules/")
@lexicon_param
@player_required_if_not_public
def rules(lexicon_name):
    return render_template("lexicon.rules.jinja", lexicon_name=lexicon_name)


@bp.get("/statistics/")
@lexicon_param
@player_required_if_not_public
def stats(lexicon_name):
    return render_template("lexicon.statistics.jinja", lexicon_name=lexicon_name)
