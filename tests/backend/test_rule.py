import pytest

from amanuensis.backend import irq
from amanuensis.db import *
from amanuensis.errors import ArgumentError

from tests.conftest import ObjectFactory


def test_create_assign(db: DbContext, make: ObjectFactory):
    """Test new index assignment creation"""
    lexicon: Lexicon = make.lexicon()
    user: User = make.user()
    mem: Membership = make.membership(lexicon_id=lexicon.id, user_id=user.id)
    char: Character = make.character(lexicon_id=lexicon.id, user_id=user.id)
    ind1: ArticleIndex = make.index(lexicon_id=lexicon.id)

    defaults: dict = {
        "db": db,
        "lexicon_id": lexicon.id,
        "character_id": char.id,
        "index_id": ind1.id,
        "turn": 1,
    }
    kwargs: dict

    # Index assignments must key to objects in the same lexicon
    lexicon2: Lexicon = make.lexicon()
    mem2: Membership = make.membership(lexicon_id=lexicon2.id, user_id=user.id)
    char2: Character = make.character(lexicon_id=lexicon2.id, user_id=user.id)
    ind2: ArticleIndex = make.index(lexicon_id=lexicon2.id)
    with pytest.raises(ArgumentError):
        kwargs = {**defaults, "index_id": ind2.id}
        irq.create(**kwargs)
    with pytest.raises(ArgumentError):
        kwargs = {**defaults, "character_id": char2.id, "index_id": ind2.id}
        irq.create(**kwargs)
    with pytest.raises(ArgumentError):
        kwargs = {**defaults, "character_id": char2.id}
        irq.create(**kwargs)
