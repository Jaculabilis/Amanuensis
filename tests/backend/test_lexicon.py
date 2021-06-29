import datetime
import time

import pytest

from amanuensis.backend import lexiq
from amanuensis.db import DbContext, Lexicon, User
from amanuensis.errors import ArgumentError
from tests.conftest import ObjectFactory


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


def test_lexicon_from(db: DbContext, make: ObjectFactory):
    """Test lexiq.from_*."""
    lexicon1: Lexicon = make.lexicon()
    lexicon2: Lexicon = make.lexicon()
    assert lexiq.try_from_name(db, lexicon1.name) == lexicon1
    assert lexiq.try_from_name(db, lexicon2.name) == lexicon2


def test_get_lexicon(db: DbContext, make: ObjectFactory):
    """Test the various scoped get functions."""
    user: User = make.user()

    public_joined: Lexicon = make.lexicon()
    public_joined.public = True
    make.membership(user_id=user.id, lexicon_id=public_joined.id)

    private_joined: Lexicon = make.lexicon()
    private_joined.public = False
    make.membership(user_id=user.id, lexicon_id=private_joined.id)

    public_open: Lexicon = make.lexicon()
    public_open.public = True
    db.session.commit()

    private_open: Lexicon = make.lexicon()
    private_open.public = False
    db.session.commit()

    get_all = list(lexiq.get_all(db))
    assert public_joined in get_all
    assert private_joined in get_all
    assert public_open in get_all
    assert private_open in get_all

    get_joined = list(lexiq.get_joined(db, user.id))
    assert public_joined in get_joined
    assert private_joined in get_joined
    assert public_open not in get_joined
    assert private_open not in get_joined

    get_public = list(lexiq.get_public(db))
    assert public_joined in get_public
    assert private_joined not in get_public
    assert public_open in get_public
    assert private_open not in get_public


def test_lexicon_update_ts(db: DbContext, make: ObjectFactory):
    """Test the update timestamp."""
    lexicon: Lexicon = make.lexicon()
    assert lexicon.created == lexicon.last_updated
    time.sleep(1)  # The update timestamp has only second-level precision
    lexicon.prompt = "New prompt, who dis"
    db.session.commit()
    assert lexicon.created != lexicon.last_updated
