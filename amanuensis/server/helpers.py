from functools import wraps
from typing import Optional

from flask import g, flash, redirect, url_for
from flask_login import current_user

from amanuensis.backend import lexiq, memq
from amanuensis.db import DbContext, Lexicon, User, Membership


def lexicon_param(route):
    """
    Wrapper for loading a route's lexicon to `g`.
    This decorator should be applied above any other decorators that reference `g.lexicon`.
    """
    @wraps(route)
    def with_lexicon(*args, **kwargs):
        db: DbContext = g.db
        name: str = kwargs.get('name')
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
                return redirect(url_for('lexicon.contents', name=lexicon.name))
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
            return redirect(url_for('lexicon.contents', name=lexicon.name))
        return route(*args, **kwargs)
    return editor_route
