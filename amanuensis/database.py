from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker


engine = create_engine('sqlite:///:memory:')

# Define naming conventions for generated constraints
metadata = MetaData(bind=engine, naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})

# Thread-safe db session
session = scoped_session(sessionmaker(bind=engine))

# Base class for ORM models
ModelBase = declarative_base(metadata=metadata)
