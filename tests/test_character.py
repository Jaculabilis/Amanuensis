import os
from urllib.parse import urlsplit

from bs4 import BeautifulSoup
from flask import Flask, url_for

from amanuensis.backend import memq, charq
from amanuensis.db import DbContext

from tests.conftest import ObjectFactory


def test_character_view(db: DbContext, app: Flask, make: ObjectFactory):
    """Test the lexicon character list, create, and edit pages."""
    username: str = f"user_{os.urandom(8).hex()}"
    charname: str = f"char_{os.urandom(8).hex()}"
    char_sig: str = f"signature_{os.urandom(8).hex()}"

    with app.test_client() as client:
        # Create the user and log in
        user = make.user(username=username, password=username)
        assert user
        user_client = make.client(user.id)
        assert client
        user_client.login(client)

        # Create a lexicon and join
        lexicon = make.lexicon()
        assert lexicon
        mem = memq.create(db, user.id, lexicon.id, is_editor=False)
        assert mem

        # The character page exists
        list_url = url_for("lexicon.characters.list", lexicon_name=lexicon.name)
        response = client.get(list_url)
        assert response.status_code == 200
        assert charname.encode("utf8") not in response.data
        assert char_sig.encode("utf8") not in response.data
        new_url = url_for("lexicon.characters.new", lexicon_name=lexicon.name)
        assert new_url.encode("utf8") in response.data

        # The character creation endpoint works
        response = client.get(new_url)
        assert response.status_code == 302
        chars = list(charq.get_in_lexicon(db, lexicon.id))
        assert len(chars) == 1
        assert chars[0].user_id == user.id
        created_redirect = response.location
        assert str(chars[0].public_id) in created_redirect

        # The character edit page works
        response = client.get(created_redirect)
        assert chars[0].name.encode("utf8") in response.data
        assert chars[0].signature.encode("utf8") in response.data
        assert b"csrf_token" in response.data

        # Submitting the edit page works
        soup = BeautifulSoup(response.data, features="html.parser")
        csrf_token = soup.find(id="csrf_token")["value"]
        assert csrf_token
        response = client.post(
            created_redirect,
            data={"name": charname, "signature": char_sig, "csrf_token": csrf_token},
        )
        assert 300 <= response.status_code <= 399

        # The character is updated
        chars = list(charq.get_in_lexicon(db, lexicon.id))
        assert len(chars) == 1
        assert chars[0].user_id == user.id
        assert chars[0].name == charname
        assert chars[0].signature == char_sig
