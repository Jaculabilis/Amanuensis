import pytest
from sqlalchemy import func

from amanuensis.db import *


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
