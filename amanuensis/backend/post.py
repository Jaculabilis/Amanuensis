"""
Post query interface
"""

import re

from sqlalchemy import select

from amanuensis.db import DbContext, Post
from amanuensis.db.models import Lexicon
from amanuensis.errors import ArgumentError


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
        raise ArgumentError("Lexicon id must be an integer.")

    # Verify user_id
    if not (isinstance(user_id, int) or user_id is None):
        raise ArgumentError("User id must be an integer.")

    # Verify body
    if not isinstance(body, str):
        raise ArgumentError("Post body must be a string.")
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
