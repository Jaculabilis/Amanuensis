"""
Index rule query interface
"""

from typing import Sequence

from sqlalchemy import select

from amanuensis.db import *
from amanuensis.errors import ArgumentError, BackendArgumentTypeError


def create(
    db: DbContext,
    lexicon_id: int,
    character_id: int,
    index_id: int,
    turn: int,
) -> ArticleIndexRule:
    """Create an index assignment."""
    # Verify argument types are correct
    if not isinstance(lexicon_id, int):
        raise BackendArgumentTypeError(int, lexicon_id=lexicon_id)
    if character_id is not None and not isinstance(character_id, int):
        raise BackendArgumentTypeError(int, character_id=character_id)
    if not isinstance(index_id, int):
        raise BackendArgumentTypeError(int, index_id=index_id)
    if not isinstance(turn, int):
        raise BackendArgumentTypeError(int, turn=turn)

    # Verify the character belongs to the lexicon
    character: Character = db(
        select(Character).where(Character.id == character_id)
    ).scalar_one_or_none()
    if not character:
        raise ArgumentError("Character does not exist")
    if character.lexicon_id != lexicon_id:
        raise ArgumentError("Character belongs to the wrong lexicon")

    # Verify the index belongs to the lexicon
    index: ArticleIndex = db(
        select(ArticleIndex).where(ArticleIndex.id == index_id)
    ).scalar_one_or_none()
    if not index:
        raise ArgumentError("Index does not exist")
    if index.lexicon_id != lexicon_id:
        raise ArgumentError("Index belongs to the wrong lexicon")

    new_assignment: ArticleIndexRule = ArticleIndexRule(
        lexicon_id=lexicon_id,
        character_id=character_id,
        index_id=index_id,
        turn=turn,
    )
    db.session.add(new_assignment)
    db.session.commit()
    return new_assignment


def get_for_lexicon(db: DbContext, lexicon_id: int) -> Sequence[ArticleIndex]:
    """Returns all index rules for a lexicon."""
    return db(
        select(ArticleIndexRule)
        .join(ArticleIndexRule.index)
        .join(ArticleIndexRule.character)
        .where(ArticleIndexRule.lexicon_id == lexicon_id)
        .order_by(ArticleIndexRule.turn, ArticleIndex.pattern, Character.name)
    ).scalars()


def update(db: DbContext, lexicon_id: int, rules: Sequence[ArticleIndexRule]) -> None:
    """
    Update the index assignments for a lexicon. An index assignment is a tuple
    of turn, index, and character. Unlike indices themselves, assignments have
    no other attributes that can be updated, so they are simply created or
    deleted based on their presence or absence in the desired rule list.
    """
    print(rules)
    extant_rules: Sequence[ArticleIndexRule] = list(get_for_lexicon(db, lexicon_id))
    for extant_rule in extant_rules:
        if not any(
            [
                extant_rule.character_id == new_rule.character_id
                and extant_rule.index_id == new_rule.index_id
                and extant_rule.turn == new_rule.turn
                for new_rule in rules
            ]
        ):
            db.session.delete(extant_rule)
    for new_rule in rules:
        if not any(
            [
                extant_rule.character_id == new_rule.character_id
                and extant_rule.index_id == new_rule.index_id
                and extant_rule.turn == new_rule.turn
                for extant_rule in extant_rules
            ]
        ):
            db.session.add(new_rule)
    db.session.commit()
