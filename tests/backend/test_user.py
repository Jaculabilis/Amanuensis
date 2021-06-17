from amanuensis.db.models import User
import pytest

from amanuensis.db import DbContext
import amanuensis.backend.user as userq
from amanuensis.errors import ArgumentError


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
    with pytest.raises(ArgumentError):
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
