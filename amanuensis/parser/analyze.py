"""
Internal module encapsulating visitors that compute metrics on articles
for verification against constraints.
"""

import re
from typing import Iterable

from amanuensis.models import LexiconModel

from .core import RenderableVisitor


class GetCitations(RenderableVisitor):
	def __init__(self):
		self.citations = []

	def ParsedArticle(self, span):
		span.recurse(self)
		return self.citations

	def CitationSpan(self, span):
		self.citations.append(span.cite_target)
		return self


class ConstraintAnalysis(RenderableVisitor):
	def __init__(self, lexicon: LexiconModel):
		self.info: Iterable[str] = []
		self.warning: Iterable[str] = []
		self.error: Iterable[str] = []

		self.word_count = 0
		self.citation_count = 0
		self.has_signature = False

	def ParsedArticle(self, span):
		# Execute over the article tree
		span.recurse(self)
		# Perform analysis
		self.info.append(f'Word count: {self.word_count}')
		if not self.has_signature:
			self.warning.append('Missing signature')
		return self

	def TextSpan(self, span):
		self.word_count += len(re.split(r'\s+', span.innertext.strip()))
		return self

	def SignatureParagraph(self, span):
		self.has_signature = True
		span.recurse(self)
		return self

	def CitationSpan(self, span):
		self.citation_count += 1
		span.recurse(self)
		return self
