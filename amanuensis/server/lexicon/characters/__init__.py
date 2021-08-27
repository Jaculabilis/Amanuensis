from flask import Blueprint, render_template, url_for
from werkzeug.utils import redirect

from amanuensis.server.helpers import lexicon_param, player_required


bp = Blueprint("characters", __name__, url_prefix="/characters", template_folder=".")


@bp.get('/')
@lexicon_param
@player_required
def characters(name):
    return render_template('characters.jinja')


@bp.post('/')
@lexicon_param
@player_required
def update(name):
    return redirect(url_for('lexicon.statistics', name=name))


# @bp.route('/', methods=['GET', 'POST'])
# @lexicon_param
# @player_required
# def characters(name):
#     return render_template("characters.jinja")
    # form = LexiconCharacterForm()
    # cid = request.args.get('cid')
    # if not cid:
    #     # No character specified, creating a new character
    #     return create_character(name, form)

    # character = g.lexicon.cfg.character.get(cid)
    # if not character:
    #     # Bad character id, abort
    #     flash('Character not found')
    #     return redirect(url_for('session.session', name=name))
    # if current_user.uid not in (character.player, g.lexicon.cfg.editor):
    #     # Only its owner and the editor can edit a character
    #     flash('Access denied')
    #     return redirect(url_for('session.session', name=name))
    # # Edit allowed
    # return edit_character(name, form, character)


# def edit_character(name, form, character):
#     if not form.is_submitted():
#         # GET, populate with values
#         return render_template(
#             'session.character.jinja', form=form.for_character(character))

#     if not form.validate():
#         # POST with invalid data, return unchanged
#         return render_template('session.character.jinja', form=form)

#     # POST with valid data, update character
#     with g.lexicon.ctx.edit_config() as cfg:
#         char = cfg.character[character.cid]
#         char.name = form.characterName.data
#         char.signature = form.defaultSignature.data
#     flash('Character updated')
#     return redirect(url_for('session.session', name=name))


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

