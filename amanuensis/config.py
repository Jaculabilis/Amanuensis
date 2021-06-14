from argparse import ArgumentParser
from typing import Optional
import os


class AmanuensisConfig:
    """Base config type. Defines config keys for subclasses to override."""

    # If CONFIG_FILE is defined, the config file it points to may override
    # config values defined on the config object itself.
    CONFIG_FILE: Optional[str] = None
    STATIC_ROOT: Optional[str] = "static"
    SECRET_KEY: Optional[str] = "secret"
    DATABASE_URI: Optional[str] = "sqlite:///:memory:"
    TESTING: bool = False


class EnvironmentConfig(AmanuensisConfig):
    """Loads config values from environment variables."""

    CONFIG_FILE = os.environ.get("AMANUENSIS_CONFIG_FILE", AmanuensisConfig.CONFIG_FILE)
    STATIC_ROOT = os.environ.get("AMANUENSIS_STATIC_ROOT", AmanuensisConfig.STATIC_ROOT)
    SECRET_KEY = os.environ.get("AMANUENSIS_SECRET_KEY", AmanuensisConfig.SECRET_KEY)
    DATABASE_URI = os.environ.get(
        "AMANUENSIS_DATABASE_URI", AmanuensisConfig.DATABASE_URI
    )
    TESTING = os.environ.get("AMANUENSIS_TESTING", "").lower() in ("true", "1")


class CommandLineConfig(AmanuensisConfig):
    """Loads config values from command line arguments."""
    def __init__(self) -> None:
        parser = ArgumentParser()
        parser.add_argument("--config-file", default=AmanuensisConfig.CONFIG_FILE)
        parser.add_argument("--static-root", default=AmanuensisConfig.STATIC_ROOT)
        parser.add_argument("--secret-key", default=AmanuensisConfig.SECRET_KEY)
        parser.add_argument("--database-uri", default=AmanuensisConfig.DATABASE_URI)
        parser.add_argument("--debug", action="store_true")
        args = parser.parse_args()

        self.CONFIG_FILE = args.config_file
        self.STATIC_ROOT = args.static_root
        self.SECRET_KEY = args.secret_key
        self.DATABASE_URI = args.database_uri
        self.TESTING = args.debug
