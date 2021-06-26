"""
pytest test fixtures
"""
import os
import pytest
import tempfile
from typing import Optional

from bs4 import BeautifulSoup
from flask.testing import FlaskClient
from sqlalchemy.orm.session import close_all_sessions

import amanuensis.backend.character as charq
import amanuensis.backend.lexicon as lexiq
import amanuensis.backend.membership as memq
import amanuensis.backend.user as userq
from amanuensis.config import AmanuensisConfig
from amanuensis.db import DbContext, User, Lexicon, Membership, Character
from amanuensis.server import get_app


@pytest.fixture
def db(request) -> DbContext:
    """Provides a fully-initialized ephemeral database."""
    db_fd, db_path = tempfile.mkstemp()
    db = DbContext(path=db_path, echo=False)
    db.create_all()

    def db_teardown():
        close_all_sessions()
        os.close(db_fd)
        os.unlink(db_path)

    request.addfinalizer(db_teardown)

    return db


class UserClient:
    """Class encapsulating user web operations."""

    def __init__(self, db: DbContext, user_id: int):
        self.db = db
        self.user_id = user_id

    def login(self, client: FlaskClient):
        """Log the user in."""
        user: Optional[User] = userq.from_id(self.db, self.user_id)
        assert user is not None

        # Set the user's password so we know what it is later
        password = os.urandom(8).hex()
        userq.password_set(self.db, user.username, password)

        # Log in
        response = client.get("/auth/login/")
        assert response.status_code == 200
        soup = BeautifulSoup(response.data, features="html.parser")
        csrf_token = soup.find(id="csrf_token")
        assert csrf_token is not None
        response = client.post(
            "/auth/login/",
            data={
                "username": user.username,
                "password": password,
                "csrf_token": csrf_token["value"],
            },
        )
        assert 300 <= response.status_code <= 399

    def logout(self, client: FlaskClient):
        """Log the user out."""
        response = client.get("/auth/logout/")
        assert 300 <= response.status_code <= 399


class ObjectFactory:
    """Factory class."""

    def __init__(self, db):
        self.db = db

    def user(self, state={"nonce": 1}, **kwargs) -> User:
        """Factory function for creating users, with valid default values."""
        default_kwargs: dict = {
            "username": f'test_user_{state["nonce"]}',
            "password": "password",
            "display_name": None,
            "email": "user@example.com",
            "is_site_admin": False,
        }
        state["nonce"] += 1
        updated_kwargs: dict = {**default_kwargs, **kwargs}
        return userq.create(self.db, **updated_kwargs)

    def lexicon(self, state={"nonce": 1}, **kwargs) -> Lexicon:
        """Factory function for creating lexicons, with valid default values."""
        default_kwargs: dict = {
            "name": f'Test_{state["nonce"]}',
            "title": None,
            "prompt": f'Test Lexicon game {state["nonce"]}',
        }
        state["nonce"] += 1
        updated_kwargs: dict = {**default_kwargs, **kwargs}
        lex = lexiq.create(self.db, **updated_kwargs)
        lex.joinable = True
        self.db.session.commit()
        return lex

    def membership(self, **kwargs) -> Membership:
        """Factory function for creating memberships, with valid default values."""
        default_kwargs: dict = {
            "is_editor": False,
        }
        updated_kwargs: dict = {**default_kwargs, **kwargs}
        return memq.create(self.db, **updated_kwargs)

    def character(self, state={"nonce": 1}, **kwargs) -> Character:
        """Factory function for creating characters, with valid default values."""
        default_kwargs: dict = {
            "name": f'Character {state["nonce"]}',
            "signature": None,
        }
        state["nonce"] += 1
        updated_kwargs: dict = {**default_kwargs, **kwargs}
        return charq.create(self.db, **updated_kwargs)

    def client(self, user_id: int) -> UserClient:
        """Factory function for user test clients."""
        return UserClient(self.db, user_id)


@pytest.fixture
def make(db: DbContext) -> ObjectFactory:
    """Fixture that provides a factory class."""
    return ObjectFactory(db)


@pytest.fixture
def lexicon_with_editor(make: ObjectFactory):
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


class TestConfig(AmanuensisConfig):
    TESTING = True
    SECRET_KEY = os.urandom(32).hex()


@pytest.fixture
def app(db: DbContext):
    """Provides an application running on top of the test database."""
    return get_app(TestConfig(), db)
