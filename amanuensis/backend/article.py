"""
Article query interface
"""

from sqlalchemy import select

from amanuensis.db import *
from amanuensis.errors import ArgumentError, BackendArgumentTypeError


def create(
    db: DbContext,
    lexicon_id: int,
    character_id: int,
    ersatz: bool = False,
) -> Article:
    """
    Create a new article in a lexicon.
    """
    # Verify argument types are correct
    if not isinstance(lexicon_id, int):
        raise BackendArgumentTypeError(int, lexicon_id=lexicon_id)
    if character_id is not None and not isinstance(character_id, int):
        raise BackendArgumentTypeError(int, character_id=character_id)

    # Check that the character belongs to the lexicon
    character: Character = db(
        select(Character).where(Character.id == character_id)
    ).scalar_one_or_none()
    if not character:
        raise ArgumentError("Character does not exist")
    if character.lexicon.id != lexicon_id:
        raise ArgumentError("Character belongs to the wrong lexicon")
    signature = character.signature if not ersatz else "~Ersatz Scrivener"

    new_article = Article(
        lexicon_id=lexicon_id,
        character_id=character_id,
        title="Article title",
        body=f"\n\n{signature}",
    )
    db.session.add(new_article)
    db.session.commit()
    return new_article
