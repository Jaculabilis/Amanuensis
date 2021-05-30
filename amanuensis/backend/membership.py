"""
Membership query interface
"""

from amanuensis.db import DbContext, Membership
from amanuensis.errors import ArgumentError


def create(
    db: DbContext,
    user_id: int,
    lexicon_id: int,
    is_editor: bool) -> Membership:
    """
    Create a new user membership in a lexicon.
    """
    # Quick argument verification
    if not isinstance(user_id, int):
        raise ArgumentError('user_id')
    if not isinstance(lexicon_id, int):
        raise ArgumentError('lexicon_id')
    if not isinstance(is_editor, bool):
        raise ArgumentError('is_editor')

    new_membership = Membership(
        user_id=user_id,
        lexicon_id=lexicon_id,
        is_editor=is_editor,
    )
    db.session.add(new_membership)
    db.session.commit()
    return new_membership
