"""
Internal module encapsulating the parsing logic for Lexipython
markdown. Parse results are represented as a hierarchy of tokens, which
can be rendered by a renderer.
"""

import re

from amanuensis.parser.helpers import normalize_title

class Renderable():
	def render(self, renderer):
		hook = getattr(renderer, type(self).__name__, None)
		if hook:
			return hook(self)
		return None

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

class CitationSpan(SpanContainer):
	"""A citation to another article"""
	def __init__(self, spans, cite_target):
		super().__init__(spans)
		# Normalize citation target
		self.cite_target = normalize_title(cite_target)
	def __str__(self):
		return f"{{{' '.join([str(span) for span in self.spans])}:{self.cite_target}}}"


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
		return SignatureParagraph(parse_paired_formatting(text[1:]))
	else:
		return BodyParagraph(parse_paired_formatting(text))

def parse_paired_formatting(text, cite=True, bold=True, italic=True):
	# Find positions of any paired formatting
	first_cite = find_pair(text, "[[", "]]", cite)
	first_bold = find_pair(text, "**", "**", bold)
	first_italic = find_pair(text, "//", "//", italic)
	# Load the possible parse handlers into the map
	handlers = {}
	handlers[first_cite] = lambda: parse_citation(text, bold=bold, italic=italic)
	handlers[first_bold] = lambda: parse_bold(text, cite=cite, italic=italic)
	handlers[first_italic] = lambda: parse_italic(text, cite=cite, bold=bold)
	# If nothing was found, move on to the next parsing step
	handlers[-1] = lambda: parse_breaks(text)
	# Choose a handler based on the earliest found result
	finds = [i for i in (first_cite, first_bold, first_italic) if i > -1]
	first = min(finds) if finds else -1
	return handlers[first]()

def find_pair(text, open_tag, close_tag, valid):
	# If skipping, return -1
	if not valid:
		return -1
	# If the open tag wasn't found, return -1
	first = text.find(open_tag)
	if first < 0:
		return -1
	# If the close tag wasn't found after the open tag, return -1
	second = text.find(close_tag, first + len(open_tag))
	if second < 0:
		return -1
	# Otherwise, the pair exists
	return first

def parse_citation(text, bold=True, italic=True):
	cite_open = text.find("[[")
	if cite_open > -1:
		cite_close = text.find("]]", cite_open + 2)
		# Since we searched for pairs from the beginning, there should be no
		# undetected pair formatting before this one, so move to the next
		# level of parsing
		spans_before = parse_breaks(text[:cite_open])
		# Continue parsing pair formatting after this one closes with all
		# three as valid choices
		spans_after = parse_paired_formatting(text[cite_close + 2:])
		# Parse inner text and skip parsing for this format pair
		text_inner = text[cite_open + 2:cite_close]
		# For citations specifically, we may need to split off a citation
		# target from the alias text
		inner_split = text_inner.split("|", 1)
		text_inner_actual, cite_target = inner_split[0], inner_split[-1]
		spans_inner = parse_paired_formatting(text_inner_actual,
			cite=False, bold=bold, italic=italic)
		citation = CitationSpan(spans_inner, cite_target)
		return spans_before + [citation] + spans_after
	# Should never happen
	return parse_breaks(text)

def parse_bold(text, cite=True, italic=True):
	bold_open = text.find("**")
	if bold_open > -1:
		bold_close = text.find("**", bold_open + 2)
		# Should be no formatting behind us
		spans_before = parse_breaks(text[:bold_open])
		# Freely parse formatting after us
		spans_after = parse_paired_formatting(text[bold_close+2:])
		# Parse inner text minus bold parsing
		text_inner = text[bold_open+2:bold_close]
		spans_inner = parse_paired_formatting(text_inner,
			cite=cite, bold=False, italic=italic)
		bold = BoldSpan(spans_inner)
		return spans_before + [bold] + spans_after
	# Should never happen
	return parse_italic(text)

def parse_italic(text, cite=True, bold=True):
	italic_open = text.find("//")
	if italic_open > -1:
		italic_close = text.find("//", italic_open + 2)
		# Should be no formatting behind us
		spans_before = parse_breaks(text[:italic_open])
		# Freely parse formatting after us
		spans_after = parse_paired_formatting(text[italic_close+2:])
		# Parse inner text minus italic parsing
		text_inner = text[italic_open+2:italic_close]
		spans_inner = parse_paired_formatting(text_inner,
			cite=cite, bold=bold, italic=False)
		italic = ItalicSpan(spans_inner)
		return spans_before + [italic] + spans_after
	# Should never happen
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
