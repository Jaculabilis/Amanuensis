import logging
from typing import Optional

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    url_for,
)
from flask_login import (
    AnonymousUserMixin,
    login_user,
    logout_user,
    login_required,
    LoginManager,
)

from amanuensis.backend import userq
from amanuensis.db import User

from .forms import LoginForm


LOG = logging.getLogger(__name__)

bp = Blueprint("auth", __name__, url_prefix="/auth", template_folder=".")


def get_login_manager() -> LoginManager:
    """Login manager factory"""
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.anonymous_user = AnonymousUserMixin

    def load_user(user_id_str: str) -> Optional[User]:
        try:
            user_id = int(user_id_str)
        except:
            return None
        return userq.try_from_id(g.db, user_id)

    login_manager.user_loader(load_user)

    return login_manager


@bp.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if not form.validate_on_submit():
        # Either the request was GET and we should render the form,
        # or the request was POST and validation failed.
        return render_template("auth.login.jinja", form=form)

    # POST with valid data
    username: str = form.username.data
    password: str = form.password.data
    user: User = userq.try_from_username(g.db, username)
    if not user or not userq.password_check(g.db, username, password):
        # Bad creds
        flash("Login not recognized")
        return redirect(url_for("auth.login"))

    # Login credentials were correct
    remember_me: bool = form.remember.data
    login_user(user, remember=remember_me)
    userq.update_logged_in(g.db, username)
    LOG.info("Logged in user {0.username} ({0.id})".format(user))
    return redirect(url_for("home.home"))


@bp.get("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home.home"))
