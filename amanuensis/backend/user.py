"""
User query interface
"""

import datetime
import re
from typing import Optional, Sequence

from sqlalchemy import select, func, update
from werkzeug.security import generate_password_hash, check_password_hash

from amanuensis.db import DbContext, User
from amanuensis.errors import ArgumentError


RE_NO_LETTERS = re.compile(r"^[0-9-_]*$")
RE_ALPHANUM_DASH_UNDER = re.compile(r"^[A-Za-z0-9-_]*$")


def create(
    db: DbContext,
    username: str,
    password: str,
    display_name: str,
    email: str,
    is_site_admin: bool,
) -> User:
    """
    Create a new user.
    """
    # Verify username
    if not isinstance(username, str):
        raise ArgumentError("Username must be a string")
    if len(username) < 3 or len(username) > 32:
        raise ArgumentError("Username must be between 3 and 32 characters")
    if RE_NO_LETTERS.match(username):
        raise ArgumentError("Username must contain a letter")
    if not RE_ALPHANUM_DASH_UNDER.match(username):
        raise ArgumentError(
            "Username may only contain alphanumerics, dash, and underscore"
        )

    # Verify password
    if not isinstance(password, str):
        raise ArgumentError("Password must be a string")

    # Verify display name
    if display_name is not None and not isinstance(display_name, str):
        raise ArgumentError("Display name must be a string")
    # If display name is not provided, use the username
    if not display_name or not display_name.strip():
        display_name = username

    # Verify email
    if not isinstance(email, str):
        raise ArgumentError("Email must be a string")

    # Query the db to make sure the username isn't taken
    if db(select(func.count(User.id)).where(User.username == username)).scalar() > 0:
        raise ArgumentError("Username is already taken")

    new_user = User(
        username=username,
        password=password,
        display_name=display_name,
        email=email,
        is_site_admin=is_site_admin,
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user


def get_all_users(db: DbContext) -> Sequence[User]:
    """Get all users."""
    return db(select(User)).scalars()


def get_user_by_id(db: DbContext, user_id: int) -> Optional[User]:
    """
    Get a user by the user's id.
    Returns None if no user was found.
    """
    user: User = db(select(User).where(User.id == user_id)).scalar_one_or_none()
    return user


def get_user_by_username(db: DbContext, username: str) -> Optional[User]:
    """
    Get a user by the user's username.
    Returns None if no user was found.
    """
    user: User = db(select(User).where(User.username == username)).scalar_one_or_none()
    return user


def password_set(db: DbContext, username: str, new_password: str) -> None:
    """Set a user's password."""
    password_hash = generate_password_hash(new_password)
    db(update(User).where(User.username == username).values(password=password_hash))
    db.session.commit()


def password_check(db: DbContext, username: str, password: str) -> bool:
    """Check if a password is correct."""
    user_password_hash: str = db(
        select(User.password).where(User.username == username)
    ).scalar_one()
    return check_password_hash(user_password_hash, password)


def update_logged_in(db: DbContext, username: str) -> None:
    """Bump the value of the last_login column for a user."""
    db(
        update(User)
        .where(User.username == username)
        .values(last_login=datetime.datetime.now(datetime.timezone.utc))
    )
    db.session.commit()
