"""
pytest test fixtures
"""
import pytest

from amanuensis.db import DbContext
import amanuensis.backend.character as charq
import amanuensis.backend.lexicon as lexiq
import amanuensis.backend.membership as memq
import amanuensis.backend.user as userq


@pytest.fixture
def db():
    """Provides an initialized database in memory."""
    db = DbContext("sqlite:///:memory:", debug=False)
    db.create_all()
    return db


@pytest.fixture
def make_user(db: DbContext):
    """Provides a factory function for creating users, with valid default values."""

    def user_factory(state={"nonce": 1}, **kwargs):
        default_kwargs = {
            "username": f'test_user_{state["nonce"]}',
            "password": "password",
            "display_name": None,
            "email": "user@example.com",
            "is_site_admin": False,
        }
        state["nonce"] += 1
        updated_kwargs = {**default_kwargs, **kwargs}
        return userq.create(db, **updated_kwargs)

    return user_factory


@pytest.fixture
def make_lexicon(db: DbContext):
    """Provides a factory function for creating lexicons, with valid default values."""

    def lexicon_factory(state={"nonce": 1}, **kwargs):
        default_kwargs = {
            "name": f'Test_{state["nonce"]}',
            "title": None,
            "prompt": f'Test Lexicon game {state["nonce"]}',
        }
        state["nonce"] += 1
        updated_kwargs = {**default_kwargs, **kwargs}
        return lexiq.create(db, **updated_kwargs)

    return lexicon_factory


@pytest.fixture
def make_membership(db: DbContext):
    """Provides a factory function for creating memberships, with valid default values."""

    def membership_factory(**kwargs):
        default_kwargs = {
            "is_editor": False,
        }
        updated_kwargs = {**default_kwargs, **kwargs}
        return memq.create(db, **updated_kwargs)

    return membership_factory


@pytest.fixture
def make_character(db: DbContext):
    """Provides a factory function for creating characters, with valid default values."""

    def character_factory(state={"nonce": 1}, **kwargs):
        default_kwargs = {
            "name": f'Character {state["nonce"]}',
            "signature": None,
        }
        state["nonce"] += 1
        updated_kwargs = {**default_kwargs, **kwargs}
        return charq.create(db, **updated_kwargs)

    return character_factory


class TestFactory:
    def __init__(self, db, **factories):
        self.db = db
        self.factories = factories

    def __getattr__(self, name):
        return self.factories[name]


@pytest.fixture
def make(
    db: DbContext, make_user, make_lexicon, make_membership, make_character
) -> TestFactory:
    """Fixture that groups all factory fixtures together."""
    return TestFactory(
        db,
        user=make_user,
        lexicon=make_lexicon,
        membership=make_membership,
        character=make_character,
    )


@pytest.fixture
def lexicon_with_editor(make):
    """Shortcut setup for a lexicon game with an editor."""
    editor = make.user()
    assert editor
    lexicon = make.lexicon()
    assert lexicon
    membership = make.membership(
        user_id=editor.id, lexicon_id=lexicon.id, is_editor=True
    )
    assert membership
    return (lexicon, editor)
