import os

import pytest

from amanuensis.backend import userq
from amanuensis.db import DbContext, User
from amanuensis.errors import ArgumentError, BackendArgumentTypeError


def test_create_user(db: DbContext):
    """Test new user creation."""
    defaults: dict = {
        "db": db,
        "username": "username",
        "password": "password",
        "display_name": "User Name",
        "email": "user@example.com",
        "is_site_admin": False,
    }
    kwargs: dict

    # Test length constraints
    with pytest.raises(ArgumentError):
        kwargs = {**defaults, "username": "me"}
        userq.create(**kwargs)
    with pytest.raises(ArgumentError):
        kwargs = {**defaults, "username": "the right honorable user-name, esquire"}
        userq.create(**kwargs)

    # Test allowed characters
    with pytest.raises(ArgumentError):
        kwargs = {**defaults, "username": "user name"}
        userq.create(**kwargs)

    # No password
    with pytest.raises(BackendArgumentTypeError):
        kwargs = {**defaults, "password": None}
        userq.create(**kwargs)

    # Valid creation works and populates fields
    new_user = userq.create(**defaults)
    assert new_user
    assert new_user.id is not None
    assert new_user.created is not None

    # No duplicate usernames
    with pytest.raises(ArgumentError):
        userq.create(**defaults)

    # Missing display name populates with username
    user2_kw: dict = {**defaults, "username": "user2", "display_name": None}
    user2: User = userq.create(**user2_kw)
    assert user2.display_name is not None


def test_user_from(db: DbContext, make):
    """Test userq.from_*."""
    user1: User = make.user()
    user2: User = make.user()
    assert userq.try_from_id(db, user1.id) == user1
    assert userq.try_from_username(db, user1.username) == user1
    assert userq.try_from_id(db, user2.id) == user2
    assert userq.try_from_username(db, user2.username) == user2


def test_user_password(db: DbContext, make):
    """Test user password functions."""
    pw1 = os.urandom(8).hex()
    pw2 = os.urandom(8).hex()
    user: User = make.user(password=pw1)
    assert userq.password_check(db, user.username, pw1)
    assert not userq.password_check(db, user.username, pw2)

    userq.password_set(db, user.username, pw2)
    assert not userq.password_check(db, user.username, pw1)
    assert userq.password_check(db, user.username, pw2)
