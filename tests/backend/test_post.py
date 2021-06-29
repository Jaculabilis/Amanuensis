import pytest

from amanuensis.backend import postq
from amanuensis.db import DbContext

from amanuensis.errors import ArgumentError


def test_create_post(db: DbContext, lexicon_with_editor):
    """Test new post creation"""
    lexicon, editor = lexicon_with_editor

    # argument dictionary for post object
    defaults: dict = {
        "db": db,
        "lexicon_id": lexicon.id,
        "user_id": editor.id,
        "body": "body",
    }
    kwargs: dict

    # ids are integers
    with pytest.raises(ArgumentError):
        kwargs = {**defaults, "user_id": "zero"}
        postq.create(**kwargs)
    with pytest.raises(ArgumentError):
        kwargs = {**defaults, "lexicon_id": "zero"}
        postq.create(**kwargs)

    # empty arguments don't work
    with pytest.raises(ArgumentError):
        kwargs = {**defaults, "lexicon_id": ""}
        postq.create(**kwargs)
    with pytest.raises(ArgumentError):
        kwargs = {**defaults, "user_id": ""}
        postq.create(**kwargs)
    with pytest.raises(ArgumentError):
        kwargs = {**defaults, "body": ""}
        postq.create(**kwargs)

    # post with only whitespace doesn't work
    with pytest.raises(ArgumentError):
        kwargs = {**defaults, "body": "    "}
        postq.create(**kwargs)

    # post creation works and populates fields
    new_post = postq.create(**defaults)
    assert new_post
    assert new_post.lexicon_id is not None
    assert new_post.user_id is not None
    assert new_post.body is not None

    # post creation works when user is None
    kwargs = {**defaults, "user_id": None}
    new_post = postq.create(**kwargs)
    assert new_post
    assert new_post.user_id is None
