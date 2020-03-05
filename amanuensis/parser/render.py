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
		return '\n'.join([child.render(self) for child in span.spans])
	def BodyParagraph(self, span):
		return f'<p>{"".join([child.render(self) for child in span.spans])}</p>'
	def SignatureParagraph(self, span):
		return ('<hr><span class="signature"><p>'
			f'{"".join([child.render(self) for child in span.spans])}'
			'</p></span>')
	def BoldSpan(self, span):
		return f'<b>{"".join([child.render(self) for child in span.spans])}</b>'
	def ItalicSpan(self, span):
		return f'<i>{"".join([child.render(self) for child in span.spans])}</i>'
	def CitationSpan(self, span):
		return f'<a href="#">{span.cite_text}</a>'
