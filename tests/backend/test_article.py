import pytest
import time

from amanuensis.backend import artiq
from amanuensis.db import DbContext, Character, Lexicon, User

from amanuensis.errors import ArgumentError
from tests.conftest import ObjectFactory


def test_create_article(db: DbContext, make: ObjectFactory):
    """Test new article creation"""
    # Create two users in a shared lexicon
    user1: User = make.user()
    user2: User = make.user()
    lexicon1: Lexicon = make.lexicon()
    make.membership(user_id=user1.id, lexicon_id=lexicon1.id)
    make.membership(user_id=user2.id, lexicon_id=lexicon1.id)
    char_l1_u1: Character = make.character(lexicon_id=lexicon1.id, user_id=user1.id)
    char_l1_u2: Character = make.character(lexicon_id=lexicon1.id, user_id=user2.id)

    # Create a lexicon that only one user is in
    lexicon2: Lexicon = make.lexicon()
    make.membership(user_id=user2.id, lexicon_id=lexicon2.id)
    char_l2_u2: Character = make.character(lexicon_id=lexicon2.id, user_id=user2.id)

    # Characters can't own articles in other lexicons
    with pytest.raises(ArgumentError):
        artiq.create(db, lexicon1.id, char_l2_u2.id)
    with pytest.raises(ArgumentError):
        artiq.create(db, lexicon2.id, char_l1_u1.id)
    with pytest.raises(ArgumentError):
        artiq.create(db, lexicon2.id, char_l1_u2.id)

    # Users can create character-owned articles
    assert artiq.create(db, lexicon1.id, char_l1_u1.id)
    assert artiq.create(db, lexicon1.id, char_l1_u2.id)
    assert artiq.create(db, lexicon2.id, char_l2_u2.id)


def test_article_update_ts(db: DbContext, make: ObjectFactory):
    """Test the update timestamp."""
    user: User = make.user()
    lexicon: Lexicon = make.lexicon()
    make.membership(user_id=user.id, lexicon_id=lexicon.id)
    char: Character = make.character(lexicon_id=lexicon.id, user_id=user.id)
    article = artiq.create(db, lexicon.id, char.id)
    created = article.last_updated
    time.sleep(1)  # The update timestamp has only second-level precision
    article.title = "New title, who dis"
    db.session.commit()
    assert created != article.last_updated
