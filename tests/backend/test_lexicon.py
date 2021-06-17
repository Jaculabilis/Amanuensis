from amanuensis.db.models import Lexicon
import datetime

import pytest

from amanuensis.db import DbContext
import amanuensis.backend.lexicon as lexiq
from amanuensis.errors import ArgumentError


def test_create_lexicon(db: DbContext):
    """Test new game creation."""
    defaults: dict = {
        "db": db,
        "name": "Test",
        "title": None,
        "prompt": "A test Lexicon game",
    }
    kwargs: dict

    # Test name constraints
    with pytest.raises(ArgumentError):
        kwargs = {**defaults, "name": None}
        lexiq.create(**kwargs)
    with pytest.raises(ArgumentError):
        kwargs = {**defaults, "name": ""}
        lexiq.create(**kwargs)
    with pytest.raises(ArgumentError):
        kwargs = {**defaults, "name": " "}
        lexiq.create(**kwargs)
    with pytest.raises(ArgumentError):
        kwargs = {**defaults, "name": ".."}
        lexiq.create(**kwargs)
    with pytest.raises(ArgumentError):
        kwargs = {**defaults, "name": "\x00"}
        lexiq.create(**kwargs)
    with pytest.raises(ArgumentError):
        kwargs = {**defaults, "name": "space in name"}
        lexiq.create(**kwargs)

    # Validate that creation populates fields, including timestamps
    before = datetime.datetime.utcnow() - datetime.timedelta(seconds=1)
    new_lexicon: Lexicon = lexiq.create(**defaults)
    after = datetime.datetime.utcnow() + datetime.timedelta(seconds=1)
    assert new_lexicon
    assert new_lexicon.id is not None
    assert new_lexicon.created is not None
    assert before < new_lexicon.created
    assert new_lexicon.created < after

    # No duplicate lexicon names
    with pytest.raises(ArgumentError):
        lexiq.create(**defaults)
