"""
User query interface
"""

import re
import uuid

from sqlalchemy import select, func

from amanuensis.db import DbContext, User
from amanuensis.errors import ArgumentError


RE_NO_LETTERS =  re.compile(r'^[0-9-_]*$')
RE_ALPHANUM_DASH_UNDER = re.compile(r'^[A-Za-z0-9-_]*$')


def create_user(
    db: DbContext,
    username: str,
    password: str,
    display_name: str,
    email: str,
    is_site_admin: bool) -> User:
    """
    Create a new user.
    """
    # Verify username
    if not isinstance(username, str):
        raise ArgumentError('Username must be a string')
    if len(username) < 3 or len(username) > 32:
        raise ArgumentError('Username must be between 3 and 32 characters')
    if RE_NO_LETTERS.match(username):
        raise ArgumentError('Username must contain a letter')
    if not RE_ALPHANUM_DASH_UNDER.match(username):
        raise ArgumentError('Username may only contain alphanumerics, dash, and underscore')

    # Verify password
    if not isinstance(password, str):
        raise ArgumentError('Password must be a string')

    # Verify display name
    if display_name is not None and not isinstance(display_name, str):
        raise ArgumentError('Display name must be a string')
    # If display name is not provided, use the username
    if not display_name or not display_name.strip():
        display_name = username

    # Verify email
    if not isinstance(email, str):
        raise ArgumentError('Email must be a string')

    # Query the db to make sure the username isn't taken
    if db.session.query(func.count(User.id)).filter(User.username == username).scalar() > 0:
        raise ArgumentError('Username is already taken')

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
