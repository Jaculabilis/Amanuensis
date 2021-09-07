from amanuensis.db.models import IndexType
import os
from urllib.parse import urlsplit

from bs4 import BeautifulSoup
from flask import Flask, url_for

from amanuensis.backend import memq, charq, indq
from amanuensis.db import DbContext

from tests.conftest import ObjectFactory


def test_index_view(db: DbContext, app: Flask, make: ObjectFactory):
    """Test the lexicon index page"""

    with app.test_client() as client:
        # Create the user and log in
        user = make.user()
        assert user
        user_client = make.client(user.id)
        assert client
        user_client.login(client)

        # Create a lexicon and join as the editor
        lexicon = make.lexicon()
        assert lexicon
        mem = memq.create(db, user.id, lexicon.id, is_editor=True)
        assert mem

        # The index settings page exists
        index_settings = url_for("lexicon.settings.index", lexicon_name=lexicon.name)
        response = client.get(index_settings)
        assert response.status_code == 200

        # Add some indices
        i1 = indq.create(db, lexicon.id, IndexType.CHAR, "ABCDE", 0, 0, 0)
        assert i1
        p1 = i1.pattern
        assert p1
        i2 = indq.create(db, lexicon.id, IndexType.RANGE, "F-M", 0, 0, 0)
        assert i2
        p2 = i2.pattern
        assert p2
        i3 = indq.create(db, lexicon.id, IndexType.CHAR, "NOPQ", 0, 0, 0)
        assert i3
        p3 = i3.pattern
        assert p3
        db.session.commit()

        # The index settings page shows the indices
        response = client.get(index_settings)
        assert response.status_code == 200
        # for i in indq.get_for_lexicon(db, lexicon.id):
        assert p1.encode("utf8") in response.data
        assert p2.encode("utf8") in response.data
        assert p3.encode("utf8") in response.data

        # Indices can be modified
        soup = BeautifulSoup(response.data, features="html.parser")
        csrf_token = soup.find(id="csrf_token")["value"]
        assert csrf_token
        response = client.post(
            index_settings,
            data={
                "csrf_token": csrf_token,
                "indices-0-index_type": "CHAR",
                "indices-0-pattern": "ABCDEF",
                "indices-0-logical_order": 0,
                "indices-0-display_order": 0,
                "indices-0-capacity": "",
                "indices-1-index_type": "PREFIX",
                "indices-1-pattern": "F-M",
                "indices-1-logical_order": 1,
                "indices-1-display_order": -1,
                "indices-1-capacity": "",
                "indices-2-index_type": "",
                "indices-2-pattern": "NOPQ",
                "indices-2-logical_order": 0,
                "indices-2-display_order": 0,
                "indices-2-capacity": "",
            },
        )
        assert 300 <= response.status_code <= 399

        updated_indices = list(indq.get_for_lexicon(db, lexicon.id))
        assert len(updated_indices) == 2
        assert updated_indices[0].index_type == IndexType.CHAR
        assert updated_indices[0].pattern == "ABCDEF"
        assert updated_indices[1].index_type == IndexType.PREFIX
        assert updated_indices[1].pattern == "F-M"
