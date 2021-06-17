from sqlalchemy import func

from amanuensis.db import *


def test_create_db(db: DbContext):
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
