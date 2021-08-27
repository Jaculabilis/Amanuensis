from typing import Optional
import uuid

from flask import Blueprint, render_template, url_for, g, flash
from werkzeug.utils import redirect

from amanuensis.backend import charq
from amanuensis.db import Character
from amanuensis.server.helpers import lexicon_param, player_required

from .forms import CharacterCreateForm


bp = Blueprint("characters", __name__, url_prefix="/characters", template_folder=".")


@bp.get('/')
@lexicon_param
@player_required
def characters(name):
    return render_template('characters.jinja')


@bp.route('/edit/<character_id>', methods=['GET', 'POST'])
@lexicon_param
@player_required
def edit(name, character_id):
    try:
        char_uuid = uuid.UUID(character_id)
    except:
        flash("Character not found")
        return redirect(url_for('lexicon.characters.characters', name=name))
    character: Optional[Character] = charq.try_from_public_id(g.db, char_uuid)
    if not character:
        flash("Character not found")
        return redirect(url_for('lexicon.characters.characters', name=name))

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
            return redirect(url_for('lexicon.characters.characters', name=name))

        else:
            # POST submitted invalid data
            return render_template('characters.edit.jinja', character=character, form=form)


# def create_character(name: str, form: LexiconCharacterForm):
#     # Characters can't be created if the game has already started
#     if g.lexicon.status != LexiconModel.PREGAME:
#         flash("Characters can't be added after the game has started")
#         return redirect(url_for('session.session', name=name))
#     # Characters can't be created beyond the per-player limit
#     player_characters = get_player_characters(g.lexicon, current_user.uid)
#     if len(list(player_characters)) >= g.lexicon.cfg.join.chars_per_player:
#         flash("Can't create more characters")
#         return redirect(url_for('session.session', name=name))

#     if not form.is_submitted():
#         # GET, populate with default values
#         return render_template(
#             'session.character.jinja', form=form.for_new())

#     if not form.validate():
#         # POST with invalid data, return unchanged
#         return render_template('session.character.jinja', form=form)

#     # POST with valid data, create character
#     char_name = form.characterName.data
#     cid = create_character_in_lexicon(current_user, g.lexicon, char_name)
#     with g.lexicon.ctx.edit_config() as cfg:
#         cfg.character[cid].signature = form.defaultSignature.data
#     flash('Character created')
#     return redirect(url_for('session.session', name=name))

