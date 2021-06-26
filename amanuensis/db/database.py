"""
Database connection setup
"""
import os

from sqlalchemy import create_engine, MetaData, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

try:
    from greenlet import getcurrent as get_ident
except ImportError:
    from threading import get_ident


# Define naming conventions for generated constraints
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

# Base class for ORM models
ModelBase = declarative_base(metadata=metadata)


class DbContext:
    """Class encapsulating connections to the database."""

    def __init__(self, path=None, uri=None, echo=False):
        """
        Create a database context.
        Exactly one of `path` and `uri` should be specified.
        """

        if path and uri:
            raise ValueError("Only one of path and uri may be specified")
        self.db_uri = uri if uri else f"sqlite:///{os.path.abspath(path)}"

        # Create an engine and enable foreign key constraints in sqlite
        self.engine = create_engine(self.db_uri, echo=echo)

        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        event.listens_for(self.engine, "connect")(set_sqlite_pragma)

        # Create a thread-safe session factory
        sm = sessionmaker(bind=self.engine)

        def add_lifecycle_hook(sm, from_state, to_state):
            def object_lifecycle_hook(_, obj):
                print(f"object moved from {from_state} to {to_state}: {obj}")

            event.listens_for(sm, f"{from_state}_to_{to_state}")(object_lifecycle_hook)

        if echo:
            add_lifecycle_hook(sm, "persistent", "detached")

        self.session = scoped_session(sm, scopefunc=get_ident)

    def __call__(self, *args, **kwargs):
        """Provides shortcut access to session.execute."""
        return self.session.execute(*args, **kwargs)

    def create_all(self):
        """Initializes the database schema."""
        ModelBase.metadata.create_all(self.engine)
