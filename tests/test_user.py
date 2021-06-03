import pytest

from amanuensis.db import DbContext
import amanuensis.backend.user as userq
from amanuensis.errors import ArgumentError


def test_create_user(db: DbContext):
    """Test new user creation."""
    kwargs = {
        'username': 'username',
        'password': 'password',
        'display_name': 'User Name',
        'email': 'user@example.com',
        'is_site_admin': False,
    }

    # Test length constraints
    with pytest.raises(ArgumentError):
        userq.create(db, **{**kwargs, 'username': 'me'})
    with pytest.raises(ArgumentError):
        userq.create(
            db, **{**kwargs, 'username': 'the right honorable user-name, esquire'}
        )
    # Test allowed characters
    with pytest.raises(ArgumentError):
        userq.create(db, **{**kwargs, 'username': 'user name'})
    # No password
    with pytest.raises(ArgumentError):
        userq.create(db, **{**kwargs, 'password': None})

    # Valid creation works and populates fields
    new_user = userq.create(db, **kwargs)
    assert new_user
    assert new_user.id is not None
    assert new_user.created is not None

    # No duplicate usernames
    with pytest.raises(ArgumentError):
        duplicate = userq.create(db, **kwargs)

    # Missing display name populates with username
    user2_kw = {**kwargs, 'username': 'user2', 'display_name': None}
    user2 = userq.create(db, **user2_kw)
    assert user2.display_name is not None
