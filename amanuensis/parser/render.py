"""
Internal module encapsulating visitors that render articles into
readable formats.
"""


class PreviewHtmlRenderer():
	def __init__(self, article_map):
		"""
		article_map maps article titles to character ids. An article
		present in the map but mapped to None is a phantom article.
		"""
		self.article_map = article_map

	def TextSpan(self, span):
		return span.innertext

	def LineBreak(self, span):
		return '<br>'

	def ParsedArticle(self, span):
		return '\n'.join(span.recurse(self))

	def BodyParagraph(self, span):
		return f'<p>{"".join(span.recurse(self))}</p>'

	def SignatureParagraph(self, span):
		return (
			'<hr><span class="signature"><p>'
			f'{"".join(span.recurse(self))}'
			'</p></span>'
		)

	def BoldSpan(self, span):
		return f'<b>{"".join(span.recurse(self))}</b>'

	def ItalicSpan(self, span):
		return f'<i>{"".join(span.recurse(self))}</i>'

	def CitationSpan(self, span):
		if span.cite_target in self.article_map:
			if self.article_map.get(span.cite_target):
				link_class = ' style="color:#0000ff"'
			else:
				link_class = ' style="color:#ff0000"'
		else:
			link_class = ' style="color:#008000"'
		return f'<a href="#"{link_class}>{"".join(span.recurse(self))}</a>'
