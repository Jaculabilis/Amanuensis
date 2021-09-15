"""
Index query interface
"""

import re
from typing import Optional, Sequence

from sqlalchemy import select

from amanuensis.db import DbContext, ArticleIndex, IndexType
from amanuensis.errors import ArgumentError, BackendArgumentTypeError


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
        raise BackendArgumentTypeError(int, lexicon_id=lexicon_id)
    if not isinstance(index_type, IndexType):
        raise BackendArgumentTypeError(IndexType, index_type=index_type)
    if not isinstance(pattern, str):
        raise BackendArgumentTypeError(str, pattern=pattern)
    if not isinstance(logical_order, int):
        raise BackendArgumentTypeError(int, logical_order=logical_order)
    if not isinstance(display_order, int):
        raise BackendArgumentTypeError(int, display_order=display_order)
    if capacity is not None and not isinstance(capacity, int):
        raise BackendArgumentTypeError(int, capacity=capacity)

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


def get_for_lexicon(db: DbContext, lexicon_id: int) -> Sequence[ArticleIndex]:
    """Returns all index rules for a lexicon."""
    return db(
        select(ArticleIndex).where(ArticleIndex.lexicon_id == lexicon_id)
    ).scalars()


def update(db: DbContext, lexicon_id: int, indices: Sequence[ArticleIndex]) -> None:
    """
    Update the indices for a lexicon. Indices are matched by type and pattern.
    An extant index not matched to an input is deleted, and an input index not
    matched to a an extant index is created. Matched indexes are updated with
    the input logical and display orders and capacity.
    """
    extant_indices: Sequence[ArticleIndex] = list(get_for_lexicon(db, lexicon_id))
    s = lambda i: f"{i.index_type}:{i.pattern}"
    for extant_index in extant_indices:
        match = None
        for new_index in indices:
            is_match = (
                extant_index.index_type == new_index.index_type
                and extant_index.pattern == new_index.pattern
            )
            if is_match:
                match = new_index
                break
        if match:
            extant_index.logical_order = new_index.logical_order
            extant_index.display_order = new_index.display_order
            extant_index.capacity = new_index.capacity
        else:
            db.session.delete(extant_index)
    for new_index in indices:
        match = None
        for extant_index in extant_indices:
            is_match = (
                extant_index.index_type == new_index.index_type
                and extant_index.pattern == new_index.pattern
            )
            if is_match:
                match = extant_index
                break
        if not match:
            new_index.lexicon_id = lexicon_id
            db.session.add(new_index)
    db.session.commit()
