import os
from urllib.parse import urlsplit

from flask import Flask

from amanuensis.db import DbContext, User, Lexicon

from .conftest import ObjectFactory, UserClient


def test_game_visibility(db: DbContext, app: Flask, make: ObjectFactory):
    """Test lexicon visibility settings."""
    user: User = make.user()
    auth: UserClient = make.client(user.id)

    public_joined: Lexicon = make.lexicon()
    public_joined.public = True
    make.membership(user_id=auth.user_id, lexicon_id=public_joined.id)
    public_joined_title = public_joined.full_title

    private_joined: Lexicon = make.lexicon()
    private_joined.public = False
    make.membership(user_id=auth.user_id, lexicon_id=private_joined.id)
    private_joined_title = private_joined.full_title

    public_open: Lexicon = make.lexicon()
    public_open.public = True
    db.session.commit()
    public_open_title = public_open.full_title

    private_open: Lexicon = make.lexicon()
    private_open.public = False
    db.session.commit()
    private_open_title = private_open.full_title

    with app.test_client() as client:
        auth.login(client)

        # Check that lexicons appear if they should
        response = client.get("/home/")
        assert response.status_code == 200
        assert public_joined_title.encode("utf8") in response.data
        assert private_joined_title.encode("utf8") in response.data
        assert public_open_title.encode("utf8") in response.data
        assert private_open_title.encode("utf8") not in response.data
