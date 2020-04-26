"""
Internal module encapsulating visitors that render articles into
readable formats.
"""

from typing import Iterable

from .core import RenderableVisitor
from .helpers import filesafe_title


class HtmlRenderer(RenderableVisitor):
	"""
	Renders an article token tree into published article HTML.
	"""
	def __init__(self, lexicon_name: str, written_articles: Iterable[str]):
		self.lexicon_name: str = lexicon_name
		self.written_articles: Iterable[str] = written_articles

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
		if span.cite_target in self.written_articles:
			link_class = ''
		else:
			link_class = ' class="phantom"'
		# link = url_for(
		# 	'lexicon.article',
		# 	name=self.lexicon_name,
		# 	title=filesafe_title(span.cite_target))
		link = (f'/lexicon/{self.lexicon_name}'
			+ f'/article/{filesafe_title(span.cite_target)}')
		return f'<a href="{link}"{link_class}>{"".join(span.recurse(self))}</a>'


class PreviewHtmlRenderer(RenderableVisitor):
	def __init__(self, lexicon):
		with lexicon.ctx.read('info') as info:
			self.article_map = {
				title: article.character
				for title, article in info.items()
			}
		self.citations = []
		self.contents = ""

	def TextSpan(self, span):
		return span.innertext

	def LineBreak(self, span):
		return '<br>'

	def ParsedArticle(self, span):
		self.contents = '\n'.join(span.recurse(self))
		return self

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
				link_class = '[extant]'
			else:
				link_class = '[phantom]'
		else:
			link_class = '[new]'
		self.citations.append(f'{span.cite_target} {link_class}')
		return f'<u>{"".join(span.recurse(self))}</u>[{len(self.citations)}]'
