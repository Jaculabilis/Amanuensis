"""
User query interface
"""

import re
import uuid

from amanuensis.db import DbContext, User
from amanuensis.errors import ArgumentError


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
    if len(username) < 3 or len(username) > 32:
        raise ArgumentError('Username must be between 3 and 32 characters')
    if re.match(r'^[0-9-_]*$', username):
        raise ArgumentError('Username must contain a letter')
    if not re.match(r'^[A-Za-z0-9-_]*$', username):
        raise ArgumentError('Username may only contain alphanumerics, dash, and underscore')
    # Verify password
    if not password:
        raise ArgumentError('Password must be provided')
    # If display name is not provided, use the username
    if not display_name.strip():
        display_name = username

    # Query the db to make sure the username isn't taken
    if db.session.query(User.username == username).count() > 0:
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
