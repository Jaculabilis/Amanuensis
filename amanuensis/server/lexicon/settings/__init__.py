from flask import Blueprint, render_template, url_for, redirect

from amanuensis.backend import *
from amanuensis.db import *
from amanuensis.server.helpers import editor_required, lexicon_param, player_required


bp = Blueprint("settings", __name__, url_prefix="/settings", template_folder=".")


@bp.get("/")
@lexicon_param
@player_required
def page(lexicon_name):
    return redirect(url_for("lexicon.settings.player", lexicon_name=lexicon_name))


@bp.get("/player/")
@lexicon_param
@player_required
def player(lexicon_name):
    return render_template("settings.jinja", lexicon_name=lexicon_name, page_name=player.__name__)


@bp.get("/general/")
@lexicon_param
@editor_required
def general(lexicon_name):
    return render_template(
        "settings.jinja", lexicon_name=lexicon_name, page_name=general.__name__
    )


@bp.get("/join/")
@lexicon_param
@editor_required
def join(lexicon_name):
    return render_template("settings.jinja", lexicon_name=lexicon_name, page_name=join.__name__)


@bp.get("/progress/")
@lexicon_param
@editor_required
def progress(lexicon_name):
    return render_template(
        "settings.jinja", lexicon_name=lexicon_name, page_name=progress.__name__
    )


@bp.get("/publish/")
@lexicon_param
@editor_required
def publish(lexicon_name):
    return render_template(
        "settings.jinja", lexicon_name=lexicon_name, page_name=publish.__name__
    )


@bp.get("/article/")
@lexicon_param
@editor_required
def article(lexicon_name):
    return render_template(
        "settings.jinja", lexicon_name=lexicon_name, page_name=article.__name__
    )
