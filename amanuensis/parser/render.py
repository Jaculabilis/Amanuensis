"""
Internal module encapsulating visitors that render articles into
readable formats.
"""


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
