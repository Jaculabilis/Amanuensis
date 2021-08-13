import pytest

from amanuensis.backend import charq
from amanuensis.db import *
from amanuensis.errors import ArgumentError, BackendArgumentTypeError


def test_create_character(db: DbContext, lexicon_with_editor, make):
    """Test creating a character."""
    lexicon: Lexicon
    user: User
    lexicon, user = lexicon_with_editor
    defaults: dict = {
        "db": db,
        "user_id": user.id,
        "lexicon_id": lexicon.id,
        "name": "Character Name",
        "signature": "Signature",
    }
    kwargs: dict

    # Bad argument types
    with pytest.raises(BackendArgumentTypeError):
        kwargs = {**defaults, "name": b"bytestring"}
        charq.create(**kwargs)
    with pytest.raises(BackendArgumentTypeError):
        kwargs = {**defaults, "name": None}
        charq.create(**kwargs)
    with pytest.raises(BackendArgumentTypeError):
        kwargs = {**defaults, "signature": b"bytestring"}
        charq.create(**kwargs)

    # Bad character name
    with pytest.raises(ArgumentError):
        kwargs = {**defaults, "name": " "}
        charq.create(**kwargs)

    # Signature is auto-populated
    kwargs = {**defaults, "signature": None}
    char = charq.create(**kwargs)
    assert char.signature is not None

    # User must be in lexicon
    new_user: User = make.user()
    with pytest.raises(ArgumentError):
        kwargs = {**defaults, "user_id": new_user.id}
        charq.create(**kwargs)


def test_character_limits(db: DbContext, lexicon_with_editor):
    """Test lexicon settings limiting character creation."""
    lexicon: Lexicon
    user: User
    lexicon, user = lexicon_with_editor

    # Set character limit to one and create a character
    lexicon.character_limit = 1
    db.session.commit()
    char1: Character = charq.create(
        db, lexicon.id, user.id, "Test Character 1", signature=None
    )
    assert char1.id, "Failed to create character 1"

    # Creating a second character should fail
    with pytest.raises(ArgumentError):
        char2: Character = charq.create(
            db, lexicon.id, user.id, "Test Character 2", signature=None
        )
        assert char2

    # Raising the limit to 2 should allow a second character
    lexicon.character_limit = 2
    db.session.commit()
    char2 = charq.create(db, lexicon.id, user.id, "Test Character 2", signature=None)
    assert char2.id, "Failed to create character 2"

    # Creating a third character should fail
    with pytest.raises(ArgumentError):
        char3: Character = charq.create(
            db, lexicon.id, user.id, "Test Character 3", signature=None
        )
        assert char3

    # Setting the limit to null should allow a third character
    lexicon.character_limit = None
    db.session.commit()
    char3 = charq.create(db, lexicon.id, user.id, "Test Character 3", signature=None)
    assert char3.id, "Failed to create character 3"
