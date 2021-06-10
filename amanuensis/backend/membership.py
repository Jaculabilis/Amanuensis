"""
Membership query interface
"""

from sqlalchemy import select, func

from amanuensis.db import DbContext, Membership
from amanuensis.db.models import Lexicon
from amanuensis.errors import ArgumentError


def create(
    db: DbContext,
    user_id: int,
    lexicon_id: int,
    is_editor: bool,
) -> Membership:
    """
    Create a new user membership in a lexicon.
    """
    # Verify argument types are correct
    if not isinstance(user_id, int):
        raise ArgumentError("user_id")
    if not isinstance(lexicon_id, int):
        raise ArgumentError("lexicon_id")
    if not isinstance(is_editor, bool):
        raise ArgumentError("is_editor")

    # Verify user has not already joined lexicon
    if (
        db(
            select(func.count(Membership.id))
            .where(Membership.user_id == user_id)
            .where(Membership.lexicon_id == lexicon_id)
        ).scalar()
        > 0
    ):
        raise ArgumentError("User is already a member of lexicon")

    # get reference to lexicon for next few checks
    lex: Lexicon = db(
        select(Lexicon).where(Lexicon.id == lexicon_id)
    ).scalar_one_or_none()
    if not lex:
        raise ArgumentError("could not find lexicon")

    # Verify lexicon is joinable
    if not lex.joinable:
        raise ArgumentError("Can't join: Lexicon is not joinable")

    # Verify lexicon is not full
    if lex.player_limit is not None:
        if (
            db(select(func.count()).where(Membership.lexicon_id == lexicon_id)).scalar()
            >= lex.player_limit
        ):
            raise ArgumentError("Can't join: Lexicon is full")

    new_membership = Membership(
        user_id=user_id,
        lexicon_id=lexicon_id,
        is_editor=is_editor,
    )
    db.session.add(new_membership)
    db.session.commit()
    return new_membership
