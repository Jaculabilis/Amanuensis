import json

from flask import Flask, g

from amanuensis.config import AmanuensisConfig
from amanuensis.db import DbContext


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
    if app.config.get("CONFIG_FILE", None):
        app.config.from_file(app.config["CONFIG_FILE"], json.load)

    # Assert that all required config values are now set
    for config_key in ("SECRET_KEY", "DATABASE_URI"):
        if not app.config.get(config_key):
            raise Exception(f"{config_key} must be defined")

    # Create the database context, if one wasn't already given
    if db is None:
        db = DbContext(app.config["DATABASE_URI"])

    # Make the database connection available to requests via g
    def db_setup():
        g.db = db
    app.before_request(db_setup)

    # Tear down the session on request teardown
    def db_teardown(response_or_exc):
        db.session.remove()
    app.teardown_appcontext(db_teardown)

    # Configure jinja options
    app.jinja_options.update(trim_blocks=True, lstrip_blocks=True)

    # Set up Flask-Login
    # TODO

    # Register blueprints
    # TODO

    def test():
        return "Hello, world!"
    app.route("/")(test)

    return app
