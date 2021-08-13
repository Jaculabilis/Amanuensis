"""
Lexicon query interface
"""

import re
from typing import Sequence, Optional

from sqlalchemy import select, func

from amanuensis.db import DbContext, Lexicon, Membership
from amanuensis.errors import ArgumentError, BackendArgumentTypeError


RE_ALPHANUM_DASH_UNDER = re.compile(r"^[A-Za-z0-9-_]*$")


def create(
    db: DbContext,
    name: str,
    title: Optional[str],
    prompt: str,
) -> Lexicon:
    """
    Create a new lexicon.
    """
    # Verify name
    if not isinstance(name, str):
        raise BackendArgumentTypeError(str, name=name)
    if not name.strip():
        raise ArgumentError("Lexicon name must not be blank")
    if not RE_ALPHANUM_DASH_UNDER.match(name):
        raise ArgumentError(
            "Lexicon name may only contain alphanumerics, dash, and underscore"
        )

    # Verify title
    if title is not None and not isinstance(title, str):
        raise BackendArgumentTypeError(str, title=title)

    # Verify prompt
    if not isinstance(prompt, str):
        raise BackendArgumentTypeError(str, prompt=prompt)

    # Query the db to make sure the lexicon name isn't taken
    if db(select(func.count(Lexicon.id)).where(Lexicon.name == name)).scalar() > 0:
        raise ArgumentError("Lexicon name is already taken")

    new_lexicon = Lexicon(
        name=name,
        title=title,
        prompt=prompt,
    )
    db.session.add(new_lexicon)
    db.session.commit()
    return new_lexicon


def get_all(db: DbContext) -> Sequence[Lexicon]:
    """Get all lexicons."""
    return db(select(Lexicon)).scalars()


def get_joined(db: DbContext, user_id: int) -> Sequence[Lexicon]:
    """Get all lexicons that a player is in."""
    return db(
        select(Lexicon).join(Lexicon.memberships).where(Membership.user_id == user_id)
    ).scalars()


def get_public(db: DbContext) -> Sequence[Lexicon]:
    """Get all publicly visible lexicons."""
    return db(select(Lexicon).where(Lexicon.public == True)).scalars()


def try_from_name(db: DbContext, name: str) -> Optional[Lexicon]:
    """Get a lexicon by its name, or None if no such lexicon was found."""
    return db(select(Lexicon).where(Lexicon.name == name)).scalar_one_or_none()
