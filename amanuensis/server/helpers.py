from functools import wraps
from typing import Optional, Any
from uuid import UUID

from flask import (
    _request_ctx_stack,
    flash,
    g,
    has_request_context,
    redirect,
    request,
    url_for,
)
from flask_login import current_user
from werkzeug.local import LocalProxy
from werkzeug.routing import BaseConverter, ValidationError

from amanuensis.backend import lexiq, memq
from amanuensis.db import DbContext, Lexicon, User, Membership


class UuidConverter(BaseConverter):
    """Converter that matches version 4 UUIDs"""
    regex = r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89aAbB][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}"

    def to_python(self, value: str) -> Any:
        try:
            return UUID(value)
        except:
            return ValidationError(f"Invalid UUID: {value}")

    def to_url(self, value: Any) -> str:
        if not isinstance(value, UUID):
            raise ValueError(f"Expected UUID, got {type(value)}: {value}")
        return str(value)


def get_current_lexicon():
    # Check if the request context is for a lexicon page
    if not has_request_context():
        return None
    lexicon_name = request.view_args.get("lexicon_name")
    if not lexicon_name:
        return None
    # Pull up the lexicon if it exists and cache it in the request context
    if not hasattr(_request_ctx_stack.top, "lexicon"):
        db: DbContext = g.db
        lexicon: Optional[Lexicon] = lexiq.try_from_name(db, lexicon_name)
        setattr(_request_ctx_stack.top, "lexicon", lexicon)
    # Return the cached lexicon
    return getattr(_request_ctx_stack.top, "lexicon", None)


current_lexicon = LocalProxy(get_current_lexicon)


def get_current_membership():
    # Base the current membership on the current user and the current lexicon
    user: User = current_user
    if not user or not user.is_authenticated:
        return None
    lexicon: Lexicon = current_lexicon
    if not lexicon:
        return None
    # Pull up the membership and cache it in the request context
    if not hasattr(_request_ctx_stack.top, "membership"):
        db: DbContext = g.db
        mem: Membership = memq.try_from_ids(db, user.id, lexicon.id)
        setattr(_request_ctx_stack.top, "membership", mem)
    # Return cached membership
    return getattr(_request_ctx_stack.top, "membership", None)


current_membership = LocalProxy(get_current_membership)


def lexicon_param(route):
    """
    Wrapper for loading a route's lexicon to `g`.
    This decorator should be applied above any other decorators that reference `g.lexicon`.
    """
    @wraps(route)
    def with_lexicon(*args, **kwargs):
        db: DbContext = g.db
        name: str = kwargs.get('lexicon_name')
        lexicon: Optional[Lexicon] = lexiq.try_from_name(db, name)
        if lexicon is None:
            flash(f"Couldn't find a lexicon with the name \"{name}\"")
            return redirect(url_for("home.home"))
        g.lexicon = lexicon
        return route(*args, **kwargs)
    return with_lexicon


def admin_required(route):
    """
    Restricts a route to users who are site admins.
    """
    @wraps(route)
    def admin_route(*args, **kwargs):
        user: User = current_user
        if not user.is_site_admin:
            flash("You must be an admin to view this page")
            return redirect(url_for('home.home'))
        return route(*args, **kwargs)
    return admin_route


def player_required(route):
    """
    Restricts a route to users who are players in the current lexicon.
    """
    @wraps(route)
    def player_route(*args, **kwargs):
        db: DbContext = g.db
        user: User = current_user
        lexicon: Lexicon = g.lexicon
        mem: Optional[Membership] = memq.try_from_ids(db, user.id, lexicon.id)
        if not mem:
            flash("You must be a player to view this page")
            if lexicon.public:
                return redirect(url_for('lexicon.contents', lexicon_name=lexicon.name))
            else:
                return redirect(url_for('home.home'))
        return route(*args, **kwargs)
    return player_route


def player_required_if_not_public(route):
    """
    Restricts a route to users who are players in the current lexicon if the lexicon is nonpublic.
    """
    @wraps(route)
    def player_route(*args, **kwargs):
        db: DbContext = g.db
        user: User = current_user
        lexicon: Lexicon = g.lexicon
        if not lexicon.public:
            mem: Optional[Membership] = memq.try_from_ids(db, user.id, lexicon.id)
            if not mem:
                flash("You must be a player to view this page")
                return redirect(url_for('home.home'))
        return route(*args, **kwargs)
    return player_route


def editor_required(route):
    """
    Restricts a route to users who are editors of the current lexicon.
    """
    @wraps(route)
    def editor_route(*args, **kwargs):
        db: DbContext = g.db
        user: User = current_user
        lexicon: Lexicon = g.lexicon
        mem: Optional[Membership] = memq.try_from_ids(db, user.id, lexicon.id)
        if not mem or not mem.is_editor:
            flash("You must be the editor to view this page")
            return redirect(url_for('lexicon.contents', lexicon_name=lexicon.name))
        return route(*args, **kwargs)
    return editor_route
