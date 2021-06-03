"""
Index query interface
"""

import re
from typing import Optional

from amanuensis.db import DbContext, ArticleIndex, IndexType
from amanuensis.errors import ArgumentError


def create(
    db: DbContext,
    lexicon_id: int,
    index_type: IndexType,
    pattern: str,
    logical_order: int,
    display_order: int,
    capacity: Optional[int],
) -> ArticleIndex:
    """
    Create a new index in a lexicon.
    """
    # Verify argument types are correct
    if not isinstance(lexicon_id, int):
        raise ArgumentError("lexicon_id")
    if not isinstance(index_type, IndexType):
        raise ArgumentError("index_type")
    if not isinstance(pattern, str):
        raise ArgumentError("pattern")
    if not isinstance(logical_order, int):
        raise ArgumentError("logical_order")
    if not isinstance(display_order, int):
        raise ArgumentError("display_order")
    if capacity is not None and not isinstance(capacity, int):
        raise ArgumentError("capacity")

    # Verify the pattern is valid for the index type:
    if index_type == IndexType.CHAR:
        if len(pattern) < 1:
            raise ArgumentError(
                f"Pattern '{pattern}' too short for index type {index_type}"
            )
    elif index_type == IndexType.RANGE:
        range_def = re.match(r"^(.)-(.)$", pattern)
        if not range_def:
            raise ArgumentError(f"Pattern '{pattern}' is not a valid range format")
        start_char, end_char = range_def.group(1), range_def.group(2)
        if start_char >= end_char:
            raise ArgumentError(
                f"Range start '{start_char}' is not before range end '{end_char}'"
            )
    elif index_type == IndexType.PREFIX:
        if len(pattern) < 1:
            raise ArgumentError(
                f"Pattern '{pattern}' too short for index type {index_type}"
            )
    elif index_type == IndexType.ETC:
        if len(pattern) < 1:
            raise ArgumentError(
                f"Pattern '{pattern}' too short for index type {index_type}"
            )

    new_index = ArticleIndex(
        lexicon_id=lexicon_id,
        index_type=index_type,
        pattern=pattern,
        logical_order=logical_order,
        display_order=display_order,
        capacity=capacity,
    )
    db.session.add(new_index)
    db.session.commit()
    return new_index
