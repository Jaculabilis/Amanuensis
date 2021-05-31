"""
pytest test fixtures
"""
import pytest

from amanuensis.db import DbContext
import amanuensis.backend.lexicon as lexiq
import amanuensis.backend.membership as memq
import amanuensis.backend.user as userq


@pytest.fixture
def db():
    """Provides an initialized database in memory."""
    db = DbContext('sqlite:///:memory:', debug=True)
    db.create_all()
    return db


@pytest.fixture
def make_user(db: DbContext):
    """Provides a factory function for creating users, with valid default values."""
    def user_factory(state={'nonce': 1}, **kwargs):
        default_kwargs = {
            'username': f'test_user_{state["nonce"]}',
            'password': 'password',
            'display_name': None,
            'email': 'user@example.com',
            'is_site_admin': False,
        }
        state['nonce'] += 1
        updated_kwargs = {**default_kwargs, **kwargs}
        return userq.create(db, **updated_kwargs)
    return user_factory


@pytest.fixture
def make_lexicon(db: DbContext):
    """Provides a factory function for creating lexicons, with valid default values."""
    def lexicon_factory(state={'nonce': 1}, **kwargs):
        default_kwargs = {
            'name': f'Test_{state["nonce"]}',
            'title': None,
            'prompt': f'Test Lexicon game {state["nonce"]}'
        }
        state['nonce'] += 1
        updated_kwargs = {**default_kwargs, **kwargs}
        return lexiq.create(db, **updated_kwargs)
    return lexicon_factory


@pytest.fixture
def make_membership(db: DbContext):
    """Provides a factory function for creating memberships, with valid default values."""
    def membership_factory(**kwargs):
        default_kwargs = {
            'is_editor': False,
        }
        updated_kwargs = {**default_kwargs, **kwargs}
        return memq.create(db, **updated_kwargs)
    return membership_factory


@pytest.fixture
def lexicon_with_editor(make_user, make_lexicon, make_membership):
    """Shortcut setup for a lexicon game with an editor."""
    editor = make_user()
    assert editor
    lexicon = make_lexicon()
    assert lexicon
    membership = make_membership(user_id=editor.id, lexicon_id=lexicon.id, is_editor=True)
    assert membership
    return (lexicon, editor)
