import datetime

import pytest

from amanuensis.db import *
import amanuensis.backend.lexicon as lexiq
from amanuensis.errors import ArgumentError

from .test_db import db


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
