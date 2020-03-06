"""
Internal module encapsulating visitors that compute metrics on articles
for verification against constraints.
"""

import re

class WordCounter():
	def TextSpan(self, span):
		return len(re.split('\s+', span.innertext.strip()))
	def LineBreak(self, span):
		return 0
	def ParsedArticle(self, span):
		return sum(span.recurse(self))
	def BodyParagraph(self, span):
		return sum(span.recurse(self))
	def SignatureParagraph(self, span):
		return sum(span.recurse(self))
	def BoldSpan(self, span):
		return sum(span.recurse(self))
	def ItalicSpan(self, span):
		return sum(span.recurse(self))
	def CitationSpan(self, span):
		return sum(span.recurse(self))
