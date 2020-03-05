"""
Internal module encapsulating the render logic for parsed articles. Rendering
is done via a rough approximation of the visitor pattern.
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
		return f'<a href="#">{span.cite_text}</a>'
