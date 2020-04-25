# Module imports
from .dict import AttrOrderedDict, ReadOnlyOrderedDict
from .directory import (
	RootConfigDirectoryContext,
	UserConfigDirectoryContext,
	LexiconConfigDirectoryContext,
	is_guid)

# Environment variable name constants
ENV_SECRET_KEY = "AMANUENSIS_SECRET_KEY"
ENV_CONFIG_DIR = "AMANUENSIS_CONFIG_DIR"
ENV_LOG_FILE = "AMANUENSIS_LOG_FILE"
ENV_LOG_FILE_SIZE = "AMANUENSIS_LOG_FILE_SIZE"
ENV_LOG_FILE_NUM = "AMANUENSIS_LOG_FILE_NUM"

__all__ = [
	AttrOrderedDict.__name__,
	ReadOnlyOrderedDict.__name__,
	RootConfigDirectoryContext.__name__,
	UserConfigDirectoryContext.__name__,
	LexiconConfigDirectoryContext.__name__,
	is_guid.__name__,
]
