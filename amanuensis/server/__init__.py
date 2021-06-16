import json
import os

from flask import Flask, g

from amanuensis.config import AmanuensisConfig, CommandLineConfig
from amanuensis.db import DbContext
import amanuensis.server.auth as auth
import amanuensis.server.home as home


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
    app.jinja_options.update(trim_blocks=True, lstrip_blocks=True)

    # Set up Flask-Login
    auth.get_login_manager().init_app(app)

    # Register blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(home.bp)

    def test():
        return "Hello, world!"

    app.route("/")(test)

    return app


def run():
    """Run the server, populating the config from the command line."""
    config = CommandLineConfig()
    app = get_app(config)
    app.run(debug=app.testing)
