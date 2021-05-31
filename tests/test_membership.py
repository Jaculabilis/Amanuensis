from amanuensis.db import DbContext
import amanuensis.backend.membership as memq


def test_create_membership(db: DbContext, make_user, make_lexicon):
    """Test joining a game."""
    # Set up a user and a lexicon
    new_user = make_user()
    assert new_user.id, 'Failed to create user'
    new_lexicon = make_lexicon()
    assert new_lexicon.id, 'Failed to create lexicon'

    # Add the user to the lexicon as an editor
    mem = memq.create(db, new_user.id, new_lexicon.id, True)
    assert mem, 'Failed to create membership'

    # Check that the user and lexicon are mutually visible in the ORM relationships
    assert new_user.memberships, 'User memberships not updated'
    assert new_lexicon.memberships, 'Lexicon memberships not updated'
    assert new_user.memberships[0].lexicon_id == new_lexicon.id
    assert new_lexicon.memberships[0].user_id == new_user.id

    # Check that the editor flag was set properly
    assert new_lexicon.memberships
