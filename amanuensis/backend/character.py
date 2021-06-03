"""
Character query interface
"""

from sqlalchemy import select, func

from amanuensis.db import *
from amanuensis.errors import ArgumentError


def create(
    db: DbContext, lexicon_id: int, user_id: int, name: str, signature: str
) -> Character:
    """
    Create a new character for a user.
    """
    # Verify argument types are correct
    if not isinstance(lexicon_id, int):
        raise ArgumentError("lexicon_id")
    if not isinstance(user_id, int):
        raise ArgumentError("user_id")
    if not isinstance(name, str):
        raise ArgumentError("name")
    if signature is not None and not isinstance(signature, str):
        raise ArgumentError("signature")

    # Verify character name is valid
    if not name.strip():
        raise ArgumentError("Character name cannot be blank")

    # If no signature is provided, use a default signature
    if not signature or not signature.strip():
        signature = f"~{name}"

    # Check that the user is a member of this lexicon
    mem: Membership = db(
        select(Membership)
        .where(Membership.user_id == user_id)
        .where(Membership.lexicon_id == lexicon_id)
    ).scalar_one_or_none()
    if not mem:
        raise ArgumentError("User is not a member of lexicon")

    # Check that this user is below the limit for creating characters
    num_user_chars = db(
        select(func.count(Character.id))
        .where(Character.lexicon_id == lexicon_id)
        .where(Character.user_id == user_id)
    ).scalar()
    if (
        mem.lexicon.character_limit is not None
        and num_user_chars >= mem.lexicon.character_limit
    ):
        raise ArgumentError("User is at character limit")

    new_character = Character(
        lexicon_id=lexicon_id,
        user_id=user_id,
        name=name,
        signature=signature,
    )
    db.session.add(new_character)
    db.session.commit()
    return new_character
