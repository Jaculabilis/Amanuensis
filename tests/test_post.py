import pytest

from amanuensis.db import *
import amanuensis.backend.lexicon as lexiq
import amanuensis.backend.user as userq
import amanuensis.backend.post as postq
import amanuensis.backend.membership as memq

from amanuensis.errors import ArgumentError

from .test_db import db

def test_create_post(db):
    """Test new post creation"""

    # Make user and lexicon
    new_user = userq.create(db, 'username', 'password', 'user', 'a@b.c', False)
    assert new_user.id, 'Failed to create user'
    new_lexicon = lexiq.create(db, 'Test', None, 'prompt')
    assert new_lexicon.id, 'Failed to create lexicon'

    # Add the user to the lexicon as an editor
    mem = memq.create(db, new_user.id, new_lexicon.id, True)
    assert mem, 'Failed to create membership'

    # argument dictionary for post object
    kwargs = {
        'lexicon_id': new_lexicon.id,
        'user_id': new_user.id,
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
