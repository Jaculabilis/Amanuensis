from amanuensis.db.models import IndexType
import pytest

from amanuensis.backend import indq
from amanuensis.db import DbContext, Lexicon

from amanuensis.errors import ArgumentError


def test_create_index(db: DbContext, make):
    """Test new index creation"""
    lexicon: Lexicon = make.lexicon()
    defaults: dict = {
        "db": db,
        "lexicon_id": lexicon.id,
        "index_type": IndexType.ETC,
        "pattern": "&c.",
        "logical_order": 0,
        "display_order": 0,
        "capacity": 0,
    }
    kwargs: dict

    # Character indexes require nonempty patterns
    with pytest.raises(ArgumentError):
        kwargs = {**defaults, "index_type": IndexType.CHAR, "pattern": ""}
        indq.create(**kwargs)
    kwargs = {**defaults, "index_type": IndexType.CHAR, "pattern": "ABC"}
    assert indq.create(**kwargs)

    # Range indexes must follow the 1-2 format
    with pytest.raises(ArgumentError):
        kwargs = {**defaults, "index_type": IndexType.RANGE, "pattern": "ABC"}
        indq.create(**kwargs)
    kwargs = {**defaults, "index_type": IndexType.RANGE, "pattern": "A-F"}
    assert indq.create(**kwargs)

    # Prefix indexes require nonempty patterns
    with pytest.raises(ArgumentError):
        kwargs = {**defaults, "index_type": IndexType.CHAR, "pattern": ""}
        indq.create(**kwargs)
    kwargs = {**defaults, "index_type": IndexType.CHAR, "pattern": "Prefix:"}
    assert indq.create(**kwargs)

    # Etc indexes require nonempty patterns
    with pytest.raises(ArgumentError):
        kwargs = {**defaults, "index_type": IndexType.CHAR, "pattern": ""}
        indq.create(**kwargs)
    kwargs = {**defaults, "index_type": IndexType.CHAR, "pattern": "&c."}
    assert indq.create(**kwargs)
