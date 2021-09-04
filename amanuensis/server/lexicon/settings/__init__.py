from flask import Blueprint, render_template, url_for, g, flash, redirect

from amanuensis.backend import *
from amanuensis.db import *
from amanuensis.server.helpers import (
    editor_required,
    lexicon_param,
    player_required,
    current_membership,
    current_lexicon,
)

from .forms import PlayerSettingsForm, SetupSettingsForm


bp = Blueprint("settings", __name__, url_prefix="/settings", template_folder=".")


@bp.get("/")
@lexicon_param
@player_required
def page(lexicon_name):
    return redirect(url_for("lexicon.settings.player", lexicon_name=lexicon_name))


@bp.route("/player/", methods=["GET", "POST"])
@lexicon_param
@player_required
def player(lexicon_name):
    form = PlayerSettingsForm()
    mem: Membership = current_membership

    if not form.is_submitted():
        # GET
        form.notify_ready.data = mem.notify_ready
        form.notify_reject.data = mem.notify_reject
        form.notify_approve.data = mem.notify_approve
        return render_template(
            "settings.jinja",
            lexicon_name=lexicon_name,
            page_name=player.__name__,
            form=form,
        )

    else:
        # POST
        if form.validate():
            # Data is valid
            mem.notify_ready = form.notify_ready.data
            mem.notify_reject = form.notify_reject.data
            mem.notify_approve = form.notify_approve.data
            g.db.session.commit()  # TODO refactor into backend
            flash("Settings saved")
            return redirect(
                url_for("lexicon.settings.player", lexicon_name=lexicon_name)
            )

        else:
            # Invalid POST data
            return render_template(
                "settings.jinja",
                lexicon_name=lexicon_name,
                page_name=player.__name__,
                form=form,
            )


@bp.route("/setup/", methods=["GET", "POST"])
@lexicon_param
@editor_required
def setup(lexicon_name):
    form = SetupSettingsForm()
    lexicon: Lexicon = current_lexicon

    if not form.is_submitted():
        # GET
        form.title.data = lexicon.title
        form.prompt.data = lexicon.prompt
        form.public.data = lexicon.public
        form.joinable.data = lexicon.joinable
        form.has_password.data = lexicon.join_password is not None
        form.turn_count.data = lexicon.turn_count
        form.player_limit.data = lexicon.player_limit
        form.character_limit.data = lexicon.character_limit
        return render_template(
            "settings.jinja",
            lexicon_name=lexicon_name,
            page_name=setup.__name__,
            form=form,
        )

    else:
        # POST
        if form.validate():
            # Data is valid
            lexicon.title = form.title.data
            lexicon.prompt = form.prompt.data
            lexicon.public = form.public.data
            lexicon.joinable = form.joinable.data
            new_password = form.password.data if form.has_password.data else None
            lexiq.password_set(g.db, lexicon.id, new_password)
            lexicon.turn_count = form.turn_count.data
            lexicon.player_limit = form.player_limit.data
            lexicon.character_limit = form.character_limit.data
            g.db.session.commit()  # TODO refactor into backend
            flash("Settings saved")
            return redirect(
                url_for("lexicon.settings.setup", lexicon_name=lexicon_name)
            )

        else:
            # Invalid POST data
            return render_template(
                "settings.jinja",
                lexicon_name=lexicon_name,
                page_name=setup.__name__,
                form=form,
            )


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
