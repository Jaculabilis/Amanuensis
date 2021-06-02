import pytest

from amanuensis.db import DbContext
import amanuensis.backend.article as artiq

from amanuensis.errors import ArgumentError


def test_create_article(db: DbContext, make):
    """Test new article creation"""
    # Create two users in a shared lexicon
    user1 = make.user()
    user2 = make.user()
    lexicon1 = make.lexicon()
    make.membership(user_id=user1.id, lexicon_id=lexicon1.id)
    make.membership(user_id=user2.id, lexicon_id=lexicon1.id)
    char1_1 = make.character(lexicon_id=lexicon1.id, user_id=user1.id)
    char1_2 = make.character(lexicon_id=lexicon1.id, user_id=user2.id)

    # Create a lexicon that only one user is in
    lexicon2 = make.lexicon()
    make.membership(user_id=user2.id, lexicon_id=lexicon2.id)
    char2_2 = make.character(lexicon_id=lexicon2.id, user_id=user2.id)

    # User cannot create article for another user's character
    with pytest.raises(ArgumentError):
        artiq.create(db, lexicon1.id, user1.id, char1_2.id)
    with pytest.raises(ArgumentError):
        artiq.create(db, lexicon1.id, user2.id, char1_1.id)

    # User cannot create article for their character in the wrong lexicon
    with pytest.raises(ArgumentError):
        artiq.create(db, lexicon1.id, user2.id, char2_2.id)
    with pytest.raises(ArgumentError):
        artiq.create(db, lexicon2.id, user2.id, char1_2.id)

    # User cannot create article in a lexicon they aren't in
    with pytest.raises(ArgumentError):
        artiq.create(db, lexicon2.id, user1.id, char1_1.id)

    # User cannot create anonymous articles in a lexicon they aren't in
    with pytest.raises(ArgumentError):
        artiq.create(db, lexicon2.id, user1.id, character_id=None)

    # Users can create character-owned articles
    assert artiq.create(db, lexicon1.id, user1.id, char1_1.id)
    assert artiq.create(db, lexicon1.id, user2.id, char1_2.id)
    assert artiq.create(db, lexicon2.id, user2.id, char2_2.id)

    # Users can create anonymous articles
    assert artiq.create(db, lexicon1.id, user1.id, character_id=None)
    assert artiq.create(db, lexicon1.id, user2.id, character_id=None)
    assert artiq.create(db, lexicon2.id, user2.id, character_id=None)
