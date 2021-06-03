"""
Article query interface
"""

from sqlalchemy import select

from amanuensis.db import *
from amanuensis.errors import ArgumentError


def create(db: DbContext, lexicon_id: int, user_id: int, character_id: int) -> Article:
    """
    Create a new article in a lexicon.
    """
    # Verify argument types are correct
    if not isinstance(lexicon_id, int):
        raise ArgumentError('lexicon_id')
    if not isinstance(user_id, int):
        raise ArgumentError('user_id')
    if character_id is not None and not isinstance(character_id, int):
        raise ArgumentError('character_id')

    # Check that the user is a member of this lexicon
    mem: Membership = db(
        select(Membership)
        .where(Membership.user_id == user_id)
        .where(Membership.lexicon_id == lexicon_id)
    ).scalar_one_or_none()
    if not mem:
        raise ArgumentError('User is not a member of lexicon')

    # If the character id is provided, check that the user owns the character
    # and the character belongs to the lexicon
    if character_id is not None:
        character: Character = db(
            select(Character).where(Character.id == character_id)
        ).scalar_one_or_none()
        if not character:
            raise ArgumentError('Character does not exist')
        if character.user.id != user_id:
            raise ArgumentError('Character is owned by the wrong player')
        if character.lexicon.id != lexicon_id:
            raise ArgumentError('Character belongs to the wrong lexicon')
        signature = character.signature
    else:
        signature = '~Ersatz Scrivener'

    new_article = Article(
        lexicon_id=lexicon_id,
        user_id=user_id,
        character_id=character_id,
        title='Article title',
        body=f'\n\n{signature}',
    )
    db.session.add(new_article)
    db.session.commit()
    return new_article
