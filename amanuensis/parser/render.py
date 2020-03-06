"""
Internal module encapsulating the render logic for parsed articles. Rendering
is done via a rough approximation of the visitor pattern.
"""

import re


class PreviewHtmlRenderer():
	def TextSpan(self, span):
		return span.innertext
	def LineBreak(self, span):
		return '<br>'
	def ParsedArticle(self, span):
		return '\n'.join(span.recurse(self))
	def BodyParagraph(self, span):
		return f'<p>{"".join(span.recurse(self))}</p>'
	def SignatureParagraph(self, span):
		return ('<hr><span class="signature"><p>'
			f'{"".join(span.recurse(self))}'
			'</p></span>')
	def BoldSpan(self, span):
		return f'<b>{"".join(span.recurse(self))}</b>'
	def ItalicSpan(self, span):
		return f'<i>{"".join(span.recurse(self))}</i>'
	def CitationSpan(self, span):
		return f'<a href="#">{"".join(span.recurse(self))}</a>'

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
