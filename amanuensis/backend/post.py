"""
Post query interface
"""

from typing import Optional, Sequence, Tuple

from sqlalchemy import select, update, func
from sqlalchemy.sql.sqltypes import DateTime

from amanuensis.db import DbContext, Post
from amanuensis.db.models import Lexicon, Membership
from amanuensis.errors import ArgumentError, BackendArgumentTypeError


def create(
    db: DbContext,
    lexicon_id: int,
    user_id: Optional[int],
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


def get_posts_for_membership(
    db: DbContext, membership_id: int
) -> Tuple[Sequence[Post], Sequence[Post]]:
    """
    Returns posts for the membership's lexicon, split into posts that
    are new since the last view and posts that were previously seen.
    """
    # Save the current timestamp, so we don't miss posts created between now
    # and when we finish looking stuff up
    now: DateTime = db(select(func.now())).scalar_one()

    # Save the previous last-seen timestamp for splitting new from old posts,
    # then update the membership with the current time
    last_seen: DateTime = db(
        select(Membership.last_post_seen).where(Membership.id == membership_id)
    ).scalar_one()
    db(
        update(Membership)
        .where(Membership.id == membership_id)
        .values(last_post_seen=now)
    )
    db.session.commit()

    # Fetch posts in two groups, new ones after the last-seen time and old ones
    # If last-seen is null, then just return everything as new
    new_posts = db(
        select(Post)
        .where(last_seen is None or Post.created > last_seen)
        .order_by(Post.created.desc())
    ).scalars()
    old_posts = db(
        select(Post)
        .where(last_seen is not None and Post.created <= last_seen)
        .order_by(Post.created.desc())
    ).scalars()

    return new_posts, old_posts
