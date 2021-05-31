import pytest

from amanuensis.db import DbContext
import amanuensis.backend.post as postq

from amanuensis.errors import ArgumentError


def test_create_post(db: DbContext, lexicon_with_editor):
    """Test new post creation"""
    lexicon, editor = lexicon_with_editor

    # argument dictionary for post object
    kwargs = {
        'lexicon_id': lexicon.id,
        'user_id': editor.id,
        'body': 'body'
    }

    # ids are integers
    with pytest.raises(ArgumentError):
        postq.create(db, **{**kwargs, 'user_id': 'zero'})
    with pytest.raises(ArgumentError):
        postq.create(db, **{**kwargs, 'lexicon_id': 'zero'})

    # empty arguments don't work
    with pytest.raises(ArgumentError):
        postq.create(db, **{**kwargs, 'lexicon_id': ''})
    with pytest.raises(ArgumentError):
        postq.create(db, **{**kwargs, 'user_id': ''})
    with pytest.raises(ArgumentError):
        postq.create(db, **{**kwargs, 'body': ''})

    # post with only whitespace doesn't work
    with pytest.raises(ArgumentError):
        postq.create(db, **{**kwargs, 'body': '    '})

    # post creation works and populates fields
    new_post = postq.create(db, **kwargs)
    assert new_post
    assert new_post.lexicon_id is not None
    assert new_post.user_id is not None
    assert new_post.body is not None

    # post creation works when user is None
    new_post = postq.create(db, **{**kwargs, 'user_id': None})
    assert new_post
    assert new_post.user_id is None
