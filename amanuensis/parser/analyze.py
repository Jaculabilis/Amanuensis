"""
Internal module encapsulating visitors that compute metrics on articles
for verification against constraints.
"""

import re

from amanuensis.parser.core import RenderableVisitor


class GetCitations(RenderableVisitor):
	def __init__(self):
		self.citations = []

	def ParsedArticle(self, span):
		span.recurse(self)
		return self.citations

	def CitationSpan(self, span):
		self.citations.append(span.cite_target)
		return self


class FeatureCounter(RenderableVisitor):
	def __init__(self):
		self.word_count = 0
		self.citation_count = 0
		self.has_signature = False

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
