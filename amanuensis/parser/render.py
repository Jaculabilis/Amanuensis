"""
Internal module encapsulating visitors that render articles into
readable formats.
"""

from flask import url_for

from amanuensis.parser.helpers import filesafe_title


class HtmlRenderer():
	"""
	Renders an article token tree into published article HTML.
	"""
	def __init__(self, lexicon_name, written_articles):
		self.lexicon_name = lexicon_name
		self.written_articles = written_articles

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
		link = f'/lexicon/{self.lexicon_name}/article/{filesafe_title(span.cite_target)}'
		return f'<a href="{link}"{link_class}>{"".join(span.recurse(self))}</a>'



class PreviewHtmlRenderer():
	def __init__(self, lexicon):
		with lexicon.ctx.read('info') as info:
			self.article_map = {
				title: article.character
				for title, article in info.items()
			}

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
