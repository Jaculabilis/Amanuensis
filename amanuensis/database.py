from sqlalchemy import create_engine, MetaData, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker


# Define naming conventions for generated constraints
metadata = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})

# Base class for ORM models
ModelBase = declarative_base(metadata=metadata)


class DbContext():
    def __init__(self, db_uri, debug=False):
        # Create an engine and enable foreign key constraints in sqlite
        self.engine = create_engine(db_uri, echo=debug)
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        # Create a thread-safe session factory
        self.session = scoped_session(sessionmaker(bind=self.engine))

    def create_all(self):
        ModelBase.metadata.create_all(self.engine)
