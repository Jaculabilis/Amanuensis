"""
Post query interface
"""

import re

from sqlalchemy import select

from amanuensis.db import DbContext, Post
from amanuensis.db.models import Lexicon
from amanuensis.errors import ArgumentError, BackendArgumentTypeError


def create(
    db: DbContext,
    lexicon_id: int,
    user_id: int,
    body: str,
) -> Post:
    """
    Create a new post
    """

    # Verify lexicon id
    if not isinstance(lexicon_id, int):
        raise BackendArgumentTypeError(int, lexicon_id=lexicon_id)

    # Verify user_id
    if user_id is not None and not isinstance(user_id, int):
        raise BackendArgumentTypeError(int, user_id=user_id)

    # Verify body
    if not isinstance(body, str):
        raise BackendArgumentTypeError(str, body=body)
    if not body.strip():
        raise ArgumentError("Post body cannot be empty.")

    # Check that the lexicon allows posting
    if not (
        db(select(Lexicon).where(Lexicon.id == lexicon_id))
        .scalar_one_or_none()
        .allow_post
    ):
        raise ArgumentError("Lexicon does not allow posting.")

    new_post = Post(lexicon_id=lexicon_id, user_id=user_id, body=body)
    db.session.add(new_post)
    db.session.commit()
    return new_post
