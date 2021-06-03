"""
Membership query interface
"""

from sqlalchemy import select, func

from amanuensis.db import DbContext, Membership
from amanuensis.errors import ArgumentError


def create(db: DbContext, user_id: int, lexicon_id: int, is_editor: bool) -> Membership:
    """
    Create a new user membership in a lexicon.
    """
    # Verify argument types are correct
    if not isinstance(user_id, int):
        raise ArgumentError('user_id')
    if not isinstance(lexicon_id, int):
        raise ArgumentError('lexicon_id')
    if not isinstance(is_editor, bool):
        raise ArgumentError('is_editor')

    # Verify user has not already joined lexicon
    if (
        db(
            select(func.count(Membership.id))
            .where(Membership.user_id == user_id)
            .where(Membership.lexicon_id == lexicon_id)
        ).scalar()
        > 0
    ):
        raise ArgumentError('User is already a member of lexicon')

    new_membership = Membership(
        user_id=user_id,
        lexicon_id=lexicon_id,
        is_editor=is_editor,
    )
    db.session.add(new_membership)
    db.session.commit()
    return new_membership
