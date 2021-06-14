from typing import Optional
import os


class AmanuensisConfig:
    """Base config type. Defines config keys for subclasses to override."""

    # If CONFIG_FILE is defined, the config file it points to may override
    # config values defined on the config object itself.
    CONFIG_FILE: Optional[str] = None
    STATIC_ROOT: Optional[str] = "static"
    SECRET_KEY: Optional[str] = None
    DATABASE_URI: Optional[str] = None
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
