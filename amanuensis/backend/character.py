"""
Character query interface
"""

from typing import Optional, Sequence

from sqlalchemy import select, func

from amanuensis.db import *
from amanuensis.errors import ArgumentError, BackendArgumentTypeError


def create(
    db: DbContext,
    lexicon_id: int,
    user_id: int,
    name: str,
    signature: Optional[str],
) -> Character:
    """
    Create a new character for a user.
    """
    # Verify argument types are correct
    if not isinstance(lexicon_id, int):
        raise BackendArgumentTypeError(int, lexicon_id=lexicon_id)
    if not isinstance(user_id, int):
        raise BackendArgumentTypeError(int, user_id=user_id)
    if not isinstance(name, str):
        raise BackendArgumentTypeError(str, name=name)
    if signature is not None and not isinstance(signature, str):
        raise BackendArgumentTypeError(str, signature=signature)

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


def get_in_lexicon(db: DbContext, lexicon_id: int) -> Sequence[Character]:
    """Get all characters in a lexicon."""
    return db(select(Character).where(Character.lexicon_id == lexicon_id)).scalars()