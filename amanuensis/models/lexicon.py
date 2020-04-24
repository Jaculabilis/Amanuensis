import time
from typing import cast

from amanuensis.config import (
	RootConfigDirectoryContext,
	LexiconConfigDirectoryContext,
	ReadOnlyOrderedDict)


class LexiconModel():
	"""Represents a lexicon in the Amanuensis config store"""
	def __init__(self, root: RootConfigDirectoryContext, lid: str):
		self._lid: str = lid
		# Creating the config context implicitly checks for existence
		self._ctx: LexiconConfigDirectoryContext = (
			cast(LexiconConfigDirectoryContext, root.lexicon[lid]))
		with self._ctx.read_config() as config:
			self._cfg: ReadOnlyOrderedDict = cast(ReadOnlyOrderedDict, config)

	def __str__(self) -> str:
		return f'<Lexicon {self.cfg.name}>'

	def __repr__(self) -> str:
		return f'<LexiconModel({self.lid})>'

	# Properties

	@property
	def lid(self) -> str:
		"""Lexicon guid"""
		return self._lid

	@property
	def ctx(self) -> LexiconConfigDirectoryContext:
		"""Lexicon config directory context"""
		return self._ctx

	@property
	def cfg(self) -> ReadOnlyOrderedDict:
		"""Cached lexicon config"""
		return self._cfg

	# Utilities

	@property
	def title(self) -> str:
		return self.cfg.get('title', f'Lexicon {self.cfg.name}')

	def log(self, message: str) -> None:
		now = int(time.time())
		with self.ctx.edit_config() as cfg:
			cfg.log.append([now, message])

	@property
	def status(self) -> str:
		if self.cfg.turn.current is None:
			return "unstarted"
		if self.cfg.turn.current > self.cfg.turn.max:
			return "completed"
		return "ongoing"
