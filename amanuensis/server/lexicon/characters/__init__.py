from typing import Optional
import uuid

from flask import Blueprint, render_template, url_for, g, flash
from flask_login import  current_user
from werkzeug.utils import redirect

from amanuensis.backend import charq
from amanuensis.db import Character
from amanuensis.server.helpers import lexicon_param, player_required

from .forms import CharacterCreateForm


bp = Blueprint("characters", __name__, url_prefix="/characters", template_folder=".")


@bp.get('/')
@lexicon_param
@player_required
def list(name):
    return render_template('characters.jinja', name=name)


@bp.route('/edit/<character_id>', methods=['GET', 'POST'])
@lexicon_param
@player_required
def edit(name, character_id):
    try:
        char_uuid = uuid.UUID(character_id)
    except:
        flash("Character not found")
        return redirect(url_for('lexicon.characters.list', name=name))
    character: Optional[Character] = charq.try_from_public_id(g.db, char_uuid)
    if not character:
        flash("Character not found")
        return redirect(url_for('lexicon.characters.list', name=name))

    form = CharacterCreateForm()

    if not form.is_submitted():
        # GET
        form.name.data = character.name
        form.signature.data = character.signature
        return render_template('characters.edit.jinja', character=character, form=form)

    else:
        # POST
        if form.validate():
            # Data is valid
            character.name = form.name.data
            character.signature = form.signature.data
            g.db.session.commit()
            return redirect(url_for('lexicon.characters.list', name=name))

        else:
            # POST submitted invalid data
            return render_template('characters.edit.jinja', character=character, form=form)


@bp.get('/new/')
@lexicon_param
@player_required
def new(name):
    dummy_name = f"{current_user.username}'s new character"
    dummy_signature = "~"
    charq.create(g.db, g.lexicon.id, current_user.id, dummy_name, dummy_signature)
    return redirect(url_for('lexicon.characters.list', name=name))
