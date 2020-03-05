"""
Internal module encapsulating the parsing logic for Lexipython
markdown. Parse results are represented as a hierarchy of tokens, which
can be rendered by a renderer.
"""

import re


class Renderable():
	def render(self, renderer):
		return getattr(renderer, type(self).__name__)(self)

class TextSpan(Renderable):
	"""An unstyled length of text"""
	def __init__(self, innertext):
		self.innertext = innertext
	def __str__(self):
		return f"[{self.innertext}]"

class LineBreak(Renderable):
	"""A line break within a paragraph"""
	def __str__(self):
		return "<break>"

class SpanContainer(Renderable):
	"""A formatting element that wraps some amount of text"""
	def __init__(self, spans):
		self.spans = spans
	def __str__(self):
		return f"[{type(self).__name__} {' '.join([str(span) for span in self.spans])}]"
	def recurse(self, renderer):
		return [child.render(renderer) for child in self.spans]

class ParsedArticle(SpanContainer):
	"""Multiple paragraphs"""

class BodyParagraph(SpanContainer):
	"""A normal paragraph"""

class SignatureParagraph(SpanContainer):
	"""A paragraph preceded by a signature mark"""

class BoldSpan(SpanContainer):
	"""A span of text inside bold marks"""

class ItalicSpan(SpanContainer):
	"""A span of text inside italic marks"""

class CitationSpan(Renderable):
	"""A citation to another article"""
	def __init__(self, cite_text, cite_target):
		self.cite_text = cite_text
		self.cite_target = cite_target
	def __str__(self):
		return f"{{{self.cite_text}:{self.cite_target}}}"


def parse_raw_markdown(text):
	# Parse each paragraph individually, as no formatting applies
	# across paragraphs
	paragraphs = re.split(r'\n\n+', text)
	parse_results = list(map(parse_paragraph, paragraphs))
	return ParsedArticle(parse_results)

def parse_paragraph(text):
	# Parse the paragraph as a span of text
	text = text.strip()
	if text and text[0] == '~':
		return SignatureParagraph(parse_citations(text[1:]))
	else:
		return BodyParagraph(parse_citations(text))

def parse_citations(text):
	cite_open = text.find("[[")
	if cite_open > -1:
		cite_close = text.find("]]", cite_open + 2)
		spans_before = parse_bold(text[:cite_open])
		spans_after = parse_citations(text[cite_close+2:])
		text_inner = text[cite_open+2:cite_close]
		alias_split = text_inner.split("|", 1)
		citation = CitationSpan(alias_split[0], alias_split[-1])
		return spans_before + [citation] + spans_after
	# No citations, just parse the regular formatting
	return parse_bold(text)

def parse_bold(text):
	bold_open = text.find("**")
	if bold_open > -1:
		bold_close = text.find("**", bold_open + 2)
		spans_before = parse_italic(text[:bold_open])
		spans_after = parse_bold(text[bold_close+2:])
		spans_inner = parse_italic(text[bold_open+2:bold_close])
		bold = BoldSpan(spans_inner)
		return spans_before + [bold] + spans_after
	return parse_italic(text)

def parse_italic(text):
	italic_open = text.find("//")
	if italic_open > -1:
		italic_close = text.find("//", italic_open + 2)
		text_before = text[:italic_open]
		text_inner = text[italic_open+2:italic_close]
		text_after = text[italic_close+2:]
		spans_before = parse_breaks(text_before)
		spans_after = parse_italic(text_after)
		spans_inner = parse_breaks(text_inner)
		italic = ItalicSpan(spans_inner)
		return spans_before + [italic] + spans_after
	return parse_breaks(text)

def parse_breaks(text):
	if not text:
		return []
	splits = list(map(TextSpan, text.split("\\\\\n")))
	spans = [splits[0]]
	for span in splits[1:]:
		spans.append(LineBreak())
		spans.append(span)
	return spans
