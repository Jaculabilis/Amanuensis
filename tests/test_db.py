import pytest
from sqlalchemy import func

from amanuensis.db import *
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
    """New user creation"""
    kwargs = {
        'username': 'username',
        'password': 'password',
        'display_name': 'User Name',
        'email': 'user@example.com',
        'is_site_admin': False
    }

    with pytest.raises(ArgumentError):
        userq.create_user(db, **{**kwargs, 'username': 'user name'})

    with pytest.raises(ArgumentError):
        userq.create_user(db, **{**kwargs, 'password': None})

    new_user = userq.create_user(db, **kwargs)
    assert new_user
    assert new_user.id is not None
    assert new_user.created is not None

    with pytest.raises(ArgumentError):
        duplicate = userq.create_user(db, **kwargs)
