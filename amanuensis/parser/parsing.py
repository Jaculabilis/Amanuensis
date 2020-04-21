"""
Internal module encapsulating a recursive descent parser for
Lexipython markdown.
"""

import re
from typing import Sequence

from amanuensis.parser.core import (
	TextSpan,
	LineBreak,
	ParsedArticle,
	BodyParagraph,
	SignatureParagraph,
	BoldSpan,
	ItalicSpan,
	CitationSpan,
	Renderable,
	SpanContainer
)

Spans = Sequence[Renderable]


def parse_raw_markdown(text: str) -> ParsedArticle:
	"""
	Parses a body of Lexipython markdown into a Renderable tree.
	"""
	# Parse each paragraph individually, as no formatting applies
	# across paragraphs
	paragraphs = re.split(r'\n\n+', text)
	parse_results = list(map(parse_paragraph, paragraphs))
	return ParsedArticle(parse_results)


def parse_paragraph(text: str) -> SpanContainer:
	# Parse the paragraph as a span of text
	text = text.strip()
	if text and text[0] == '~':
		return SignatureParagraph(parse_paired_formatting(text[1:]))
	else:
		return BodyParagraph(parse_paired_formatting(text))


def parse_paired_formatting(
		text: str,
		cite: bool = True,
		bold: bool = True,
		italic: bool = True) -> Spans:
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


def find_pair(
		text: str,
		open_tag: str,
		close_tag: str,
		valid: bool) -> int:
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


def parse_citation(text: str, bold: bool = True, italic: bool = True) -> Spans:
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
		return [*spans_before, citation, *spans_after]
	# Should never happen
	return parse_breaks(text)


def parse_bold(text: str, cite: bool = True, italic: bool = True) -> Spans:
	bold_open = text.find("**")
	if bold_open > -1:
		bold_close = text.find("**", bold_open + 2)
		# Should be no formatting behind us
		spans_before = parse_breaks(text[:bold_open])
		# Freely parse formatting after us
		spans_after = parse_paired_formatting(text[bold_close + 2:])
		# Parse inner text minus bold parsing
		text_inner = text[bold_open + 2:bold_close]
		spans_inner = parse_paired_formatting(text_inner,
			cite=cite, bold=False, italic=italic)
		bold = BoldSpan(spans_inner)
		return [*spans_before, bold, *spans_after]
	# Should never happen
	return parse_italic(text)


def parse_italic(text: str, cite: bool = True, bold: bool = True) -> Spans:
	italic_open = text.find("//")
	if italic_open > -1:
		italic_close = text.find("//", italic_open + 2)
		# Should be no formatting behind us
		spans_before = parse_breaks(text[:italic_open])
		# Freely parse formatting after us
		spans_after = parse_paired_formatting(text[italic_close + 2:])
		# Parse inner text minus italic parsing
		text_inner = text[italic_open + 2:italic_close]
		spans_inner = parse_paired_formatting(text_inner,
			cite=cite, bold=bold, italic=False)
		italic = ItalicSpan(spans_inner)
		return [*spans_before, italic, *spans_after]
	# Should never happen
	return parse_breaks(text)


def parse_breaks(text: str) -> Spans:
	if not text:
		return []
	splits: Spans = list(map(TextSpan, text.split("\\\\\n")))
	spans: Spans = [
		splits[i // 2] if i % 2 == 0 else LineBreak()
		for i in range(0, 2 * len(splits) - 1)
	]
	return spans
