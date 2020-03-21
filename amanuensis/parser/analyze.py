"""
Internal module encapsulating visitors that compute metrics on articles
for verification against constraints.
"""

import re

class FeatureCounter():
	def __init__(self):
		self.word_count = 0
		self.citation_count = 0
		self.has_signature = False

	def TextSpan(self, span):
		self.word_count += len(re.split('\s+', span.innertext.strip()))
		return self

	def LineBreak(self, span):
		return self

	def ParsedArticle(self, span):
		span.recurse(self)
		return self

	def BodyParagraph(self, span):
		span.recurse(self)
		return self

	def SignatureParagraph(self, span):
		self.has_signature = True
		span.recurse(self)
		return self

	def BoldSpan(self, span):
		span.recurse(self)
		return self

	def ItalicSpan(self, span):
		span.recurse(self)
		return self

	def CitationSpan(self, span):
		self.citation_count += 1
		span.recurse(self)
		return self