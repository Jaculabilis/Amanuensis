from datetime import datetime, timezone
import json
import os

from flask import Flask, g, url_for, redirect

from amanuensis.backend import *
from amanuensis.config import AmanuensisConfig, CommandLineConfig
from amanuensis.db import DbContext
from amanuensis.parser import filesafe_title
import amanuensis.server.auth as auth
from amanuensis.server.helpers import UuidConverter, current_lexicon, current_membership
import amanuensis.server.home as home
import amanuensis.server.lexicon as lexicon


def date_format(dt: datetime, formatstr="%Y-%m-%d %H:%M:%S%z") -> str:
    """Convert datetime to human-readable string"""
    if dt is None:
        return "never"
    # Cast db time to UTC, then convert to local timezone
    adjusted = dt.replace(tzinfo=timezone.utc).astimezone()
    return adjusted.strftime(formatstr)


def article_link(title):
    """Get the url for a lexicon by its title"""
    return url_for(
        'lexicon.article',
        lexicon_name=g.lexicon.name,
        title=filesafe_title(title))


def get_app(
    config: AmanuensisConfig,
    db: DbContext = None,
) -> Flask:
    """Application factory"""
    # Create the Flask object
    app = Flask(__name__, template_folder=".", static_folder=config.STATIC_ROOT)

    # Load keys from the config object
    app.config.from_object(config)

    # If a config file is now specified, also load keys from there
    if config_path := app.config.get("CONFIG_FILE", None):
        app.config.from_file(os.path.abspath(config_path), json.load)

    # Assert that all required config values are now set
    for config_key in ("SECRET_KEY", "DATABASE_URI"):
        if not app.config.get(config_key):
            raise Exception(f"{config_key} must be defined")

    # Create the database context, if one wasn't already given
    if db is None:
        db = DbContext(uri=app.config["DATABASE_URI"])

    # Make the database connection available to requests via g
    def db_setup():
        g.db = db

    app.before_request(db_setup)

    # Tear down the session on request teardown
    def db_teardown(response_or_exc):
        db.session.remove()

    app.teardown_appcontext(db_teardown)

    # Configure jinja options
    def add_jinja_context():
        return {
            "db": db,
            "lexiq": lexiq,
            "userq": userq,
            "memq": memq,
            "charq": charq,
            "indq": indq,
            "postq": postq,
            "current_lexicon": current_lexicon,
            "current_membership": current_membership
        }

    app.jinja_options.update(trim_blocks=True, lstrip_blocks=True)
    app.template_filter("date")(date_format)
    app.template_filter("articlelink")(article_link)
    app.context_processor(add_jinja_context)

    # Set up uuid route converter
    app.url_map.converters["uuid"] = UuidConverter

    # Set up Flask-Login
    auth.get_login_manager().init_app(app)

    # Register blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(home.bp)
    app.register_blueprint(lexicon.bp)

    # Add a root redirect
    def root():
        return redirect(url_for("home.home"))

    app.route("/")(root)

    return app


def run():
    """Run the server, populating the config from the command line."""
    config = CommandLineConfig()
    app = get_app(config)
    app.run(debug=app.testing)
