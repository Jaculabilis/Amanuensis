from typing import Sequence

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

from .forms import (
    PlayerSettingsForm,
    SetupSettingsForm,
    IndexSchemaForm,
    IndexAssignmentsForm,
)


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
        form.allow_post.data = lexicon.allow_post
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
            lexicon.allow_post = form.allow_post.data
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


@bp.get("/index/")
@lexicon_param
@editor_required
def index(lexicon_name):
    # Get the current indices
    indices: Sequence[ArticleIndex] = indq.get_for_lexicon(g.db, current_lexicon.id)
    index_data = [
        {
            "index_type": str(index.index_type),
            "pattern": index.pattern,
            "logical_order": index.logical_order,
            "display_order": index.display_order,
            "capacity": index.capacity,
        }
        for index in indices
    ]
    # Add a blank index to allow for adding rules
    index_data.append(
        {
            "index_type": "",
            "pattern": None,
            "logical_order": None,
            "display_order": None,
            "capacity": None,
        }
    )
    form = IndexSchemaForm(indices=index_data)
    return render_template(
        "settings.jinja", lexicon_name=lexicon_name, page_name=index.__name__, form=form
    )


@bp.post("/index/")
@lexicon_param
@editor_required
def index_post(lexicon_name):
    # Initialize the form
    form = IndexSchemaForm()
    if form.validate():
        # Valid data, strip out all indices with the blank type
        indices = [
            ArticleIndex(
                lexicon_id=current_lexicon.id,
                index_type=index_def.index_type.data,
                pattern=index_def.pattern.data,
                logical_order=index_def.logical_order.data,
                display_order=index_def.display_order.data,
                capacity=index_def.capacity.data,
            )
            for index_def in form.indices.entries
            if index_def.index_type.data
        ]
        indq.update(g.db, current_lexicon.id, indices)
        return redirect(url_for("lexicon.settings.index", lexicon_name=lexicon_name))
    else:
        # Invalid data
        return render_template(
            "settings.jinja",
            lexicon_name=lexicon_name,
            page_name=index.__name__,
            form=form,
        )


@bp.get("/assign/")
@lexicon_param
@editor_required
def assign(lexicon_name):
    # Get the current assignments
    rules: Sequence[ArticleIndexRule] = list(
        irq.get_for_lexicon(g.db, current_lexicon.id)
    )
    rule_data = [
        {
            "turn": rule.turn,
            "index": rule.index.name,
            "character": str(rule.character.public_id),
        }
        for rule in rules
    ]
    # Add a blank rule to allow for adding rules
    rule_data.append(
        {
            "turn": 0,
            "index": "",
            "character": "",
        }
    )
    form = IndexAssignmentsForm(rules=rule_data)
    form.populate(current_lexicon)
    return render_template(
        "settings.jinja",
        lexicon_name=lexicon_name,
        page_name=assign.__name__,
        form=form,
    )


@bp.post("/assign/")
@lexicon_param
@editor_required
def assign_post(lexicon_name):
    # Initialize the form
    form = IndexAssignmentsForm()
    form.populate(current_lexicon)
    if form.validate():
        # Valid data
        indices = list(current_lexicon.indices)
        characters = list(current_lexicon.characters)
        rules = []
        for rule_def in form.rules.entries:
            # Strip out all assignments with no character
            if not rule_def.character.data:
                continue
            # Look up the necessary ids from the public representations
            character = [
                c for c in characters if c.public_id == rule_def.character.data
            ]
            if not character:
                return redirect(
                    url_for("lexicon.settings.assign", lexicon_name=lexicon_name)
                )
            index = [i for i in indices if i.name == rule_def.index.data]
            if not index:
                return redirect(
                    url_for("lexicon.settings.assign", lexicon_name=lexicon_name)
                )
            rules.append(
                ArticleIndexRule(
                    lexicon_id=current_lexicon.id,
                    character_id=character[0].id,
                    index_id=index[0].id,
                    turn=rule_def.turn.data,
                )
            )
        irq.update(g.db, current_lexicon.id, rules)
        return redirect(url_for("lexicon.settings.assign", lexicon_name=lexicon_name))
    else:
        # Invalid data
        return render_template(
            "settings.jinja",
            lexicon_name=lexicon_name,
            page_name=assign.__name__,
            form=form,
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
