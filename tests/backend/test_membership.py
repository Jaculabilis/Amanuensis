import pytest

from sqlalchemy import select

from amanuensis.backend import memq
from amanuensis.db import *
from amanuensis.errors import ArgumentError


def test_create_membership(db: DbContext, make):
    """Test joining a game."""
    # Set up a user and a lexicon
    new_user: User = make.user()
    assert new_user.id, "Failed to create user"
    new_lexicon: Lexicon = make.lexicon()
    assert new_lexicon.id, "Failed to create lexicon"

    # Joining doesn't work when joinable is false
    new_lexicon.joinable = False
    db.session.commit()
    with pytest.raises(ArgumentError):
        memq.create(db, new_user.id, new_lexicon.id, True)

    # Joining works when joinable is true
    new_lexicon.joinable = True
    db.session.commit()
    mem: Membership = memq.create(db, new_user.id, new_lexicon.id, True)
    assert mem, "Failed to create membership"

    # Check that the user and lexicon are mutually visible in the ORM relationships
    assert any(map(lambda mem: mem.lexicon == new_lexicon, new_user.memberships))
    assert any(map(lambda mem: mem.user == new_user, new_lexicon.memberships))

    # Check that the editor flag was set properly
    editor: User = db(
        select(User)
        .join(User.memberships)
        .join(Membership.lexicon)
        .where(Lexicon.id == new_lexicon.id)
        .where(Membership.is_editor == True)
    ).scalar_one()
    assert editor is not None
    assert isinstance(editor, User)
    assert editor.id == new_user.id

    # Check that joining twice is not allowed
    with pytest.raises(ArgumentError):
        memq.create(db, new_user.id, new_lexicon.id, False)

    # Check that joining full lexicon not allowed
    new_lexicon.player_limit = 1
    db.session.commit()
    two_user: User = make.user()

    with pytest.raises(ArgumentError):
        memq.create(db, two_user.id, new_lexicon.id, False)

    new_lexicon.player_limit = 2
    db.session.commit()
    mem2: Membership = memq.create(db, two_user.id, new_lexicon.id, False)
    assert mem2, "Failed to join lexicon with open player slots"
