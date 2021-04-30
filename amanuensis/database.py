from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker


engine = create_engine('sqlite:///:memory:')

# Thread-safe db session
session = scoped_session(sessionmaker(bind=engine))

# Base class for ORM models
ModelBase = declarative_base(engine)
