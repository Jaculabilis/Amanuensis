from sqlalchemy import create_engine, MetaData, event, TypeDecorator, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
import sqlite3
import uuid


# Register GUID as a known type with sqlite
sqlite3.register_converter('GUID', lambda h: uuid.UUID(hex=h))
sqlite3.register_adapter(uuid.UUID, lambda u: u.hex)

class Uuid(TypeDecorator):
	"""
	A uuid backed by a char(32) field in sqlite.
	"""
	impl = CHAR(32)

	def process_bind_param(self, value, dialect):
		if value is None:
			return value
		elif not isinstance(value, uuid.UUID):
			return f'{uuid.UUID(value).int:32x}'
		else:
			return f'{value.int:32x}'

	def process_result_value(self, value, dialect):
		if value is None:
			return value
		elif not isinstance(value, uuid.UUID):
			return uuid.UUID(value)
		else:
			return value

engine = create_engine('sqlite:///:memory:', connect_args={'detect_types': sqlite3.PARSE_DECLTYPES})

# Enable foreign key constraints
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

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
