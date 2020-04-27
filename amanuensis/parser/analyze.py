"""
Internal module encapsulating visitors that compute metrics on articles
for verification against constraints.
"""

import re
from typing import List

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
		self.info: List[str] = []
		self.warning: List[str] = []
		self.error: List[str] = []

		self.word_count = 0
		self.citation_count = 0
		self.signatures = 0

	def TextSpan(self, span):
		self.word_count += len(re.split(r'\s+', span.innertext.strip()))
		return self

	def SignatureParagraph(self, span):
		self.signatures += 1
		span.recurse(self)
		return self

	def CitationSpan(self, span):
		self.citation_count += 1
		span.recurse(self)
		return self
