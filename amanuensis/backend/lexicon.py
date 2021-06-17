"""
Lexicon query interface
"""

import re
from typing import Sequence, Optional

from sqlalchemy import select, func

from amanuensis.db import DbContext, Lexicon, Membership
from amanuensis.errors import ArgumentError


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
        raise ArgumentError("Lexicon name must be a string")
    if not name.strip():
        raise ArgumentError("Lexicon name must not be blank")
    if not RE_ALPHANUM_DASH_UNDER.match(name):
        raise ArgumentError(
            "Lexicon name may only contain alphanumerics, dash, and underscore"
        )

    # Verify title
    if title is not None and not isinstance(name, str):
        raise ArgumentError("Lexicon name must be a string")

    # Verify prompt
    if not isinstance(prompt, str):
        raise ArgumentError("Lexicon prompt must be a string")

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


def from_name(db: DbContext, name: str) -> Lexicon:
    """Get a lexicon by its name."""
    return db(select(Lexicon).where(Lexicon.name == name)).scalar_one()


def get_all(db: DbContext) -> Sequence[Lexicon]:
    """Get all lexicons."""
    return db(select(Lexicon)).scalars()


def get_joined(db: DbContext, user_id: int) -> Sequence[Lexicon]:
    """Get all lexicons that a player is in."""
    return db(select(Lexicon).join(Lexicon.memberships).where(Membership.user_id == user_id)).scalars()


def get_public(db: DbContext) -> Sequence[Lexicon]:
    """Get all publicly visible lexicons."""
    return db(select(Lexicon).where(Lexicon.public == True)).scalars()
