import datetime

import pytest
from sqlalchemy import func

from amanuensis.db import *
import amanuensis.backend.lexicon as lexiq
import amanuensis.backend.user as userq
from amanuensis.errors import ArgumentError


@pytest.fixture
def db():
    db = DbContext('sqlite:///:memory:', debug=True)
    db.create_all()
    return db


def test_create(db):
    """Simple test that the database creates fine from scratch."""
    assert db.session.query(func.count(User.id)).scalar() == 0
    assert db.session.query(func.count(Lexicon.id)).scalar() == 0
    assert db.session.query(func.count(Membership.id)).scalar() == 0
    assert db.session.query(func.count(Character.id)).scalar() == 0
    assert db.session.query(func.count(Article.id)).scalar() == 0
    assert db.session.query(func.count(ArticleIndex.id)).scalar() == 0
    assert db.session.query(func.count(ArticleIndexRule.id)).scalar() == 0
    assert db.session.query(func.count(ArticleContentRule.id)).scalar() == 0
    assert db.session.query(func.count(Post.id)).scalar() == 0


def test_create_user(db):
    """Test new user creation."""
    kwargs = {
        'username': 'username',
        'password': 'password',
        'display_name': 'User Name',
        'email': 'user@example.com',
        'is_site_admin': False
    }

    # Test length constraints
    with pytest.raises(ArgumentError):
        userq.create_user(db, **{**kwargs, 'username': 'me'})
    with pytest.raises(ArgumentError):
        userq.create_user(db, **{**kwargs, 'username': 'the right honorable user-name, esquire'})
    # Test allowed characters
    with pytest.raises(ArgumentError):
        userq.create_user(db, **{**kwargs, 'username': 'user name'})
    # No password
    with pytest.raises(ArgumentError):
        userq.create_user(db, **{**kwargs, 'password': None})

    # Valid creation works and populates fields
    new_user = userq.create_user(db, **kwargs)
    assert new_user
    assert new_user.id is not None
    assert new_user.created is not None

    # No duplicate usernames
    with pytest.raises(ArgumentError):
        duplicate = userq.create_user(db, **kwargs)

    # Missing display name populates with username
    user2_kw = {**kwargs, 'username': 'user2', 'display_name': None}
    user2 = userq.create_user(db, **user2_kw)
    assert user2.display_name is not None


def test_create_lexicon(db):
    """Test new game creation."""
    kwargs = {
        'name': 'Test',
        'title': None,
        'prompt': 'A test Lexicon game'
    }
    # Test name constraints
    with pytest.raises(ArgumentError):
        lexiq.create_lexicon(db, **{**kwargs, 'name': None})
    with pytest.raises(ArgumentError):
        lexiq.create_lexicon(db, **{**kwargs, 'name': ''})
    with pytest.raises(ArgumentError):
        lexiq.create_lexicon(db, **{**kwargs, 'name': ' '})
    with pytest.raises(ArgumentError):
        lexiq.create_lexicon(db, **{**kwargs, 'name': '..'})
    with pytest.raises(ArgumentError):
        lexiq.create_lexicon(db, **{**kwargs, 'name': '\x00'})
    with pytest.raises(ArgumentError):
        lexiq.create_lexicon(db, **{**kwargs, 'name': 'space in name'})

    # Validate that creation populates fields, including timestamps
    before = datetime.datetime.utcnow() - datetime.timedelta(seconds=1)
    new_lexicon = lexiq.create_lexicon(db, **kwargs)
    after = datetime.datetime.utcnow() + datetime.timedelta(seconds=1)
    assert new_lexicon
    assert new_lexicon.id is not None
    assert new_lexicon.created is not None
    assert before < new_lexicon.created
    assert new_lexicon.created < after

    # No duplicate lexicon names
    with pytest.raises(ArgumentError):
        duplicate = lexiq.create_lexicon(db, **kwargs)
