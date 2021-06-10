"""
Internal module encapsulating a recursive descent parser for
Lexipython markdown.
"""

import re
from typing import Sequence

from .core import (
    TextSpan,
    LineBreak,
    ParsedArticle,
    BodyParagraph,
    SignatureParagraph,
    BoldSpan,
    ItalicSpan,
    CitationSpan,
    Renderable,
    SpanContainer,
)

Spans = Sequence[Renderable]


def parse_raw_markdown(text: str) -> ParsedArticle:
    """
    Parses a body of Lexipython markdown into a Renderable tree.
    """
    # Parse each paragraph individually, as no formatting applies
    # across paragraphs
    paragraphs = re.split(r"\n\n+", text)
    parse_results = list(map(parse_paragraph, paragraphs))
    return ParsedArticle(parse_results)


def parse_paragraph(text: str) -> SpanContainer:
    """
    Parses a block of text into a paragraph object.
    """
    # Parse the paragraph as a span of text
    text = text.strip()
    if text and text[0] == "~":
        return SignatureParagraph(parse_paired_formatting(text[1:]))
    else:
        return BodyParagraph(parse_paired_formatting(text))


def parse_paired_formatting(
    text: str,
    in_cite: bool = False,
    in_bold: bool = False,
    in_italic: bool = False,
) -> Spans:
    """
    Parses citations, bolds, and italics, which can be nested inside each other.
    A single type cannot nest inside itself, which is controlled by setting the
    flag parameters to False.
    """
    # Find positions of any paired formatting
    next_cite = find_pair(text, "[[", "]]") if not in_cite else -1
    next_bold = find_pair(text, "**", "**") if not in_bold else -1
    next_italic = find_pair(text, "//", "//") if not in_italic else -1
    # Create a map from a formatting mark's distance to its parse handler
    handlers = {}
    handlers[next_cite] = lambda: parse_citation(
        text, in_bold=in_bold, in_italic=in_italic
    )
    handlers[next_bold] = lambda: parse_bold(
        text, in_cite=in_cite, in_italic=in_italic
    )
    handlers[next_italic] = lambda: parse_italic(
        text, in_cite=in_cite, in_bold=in_bold
    )
    # Map the next parsing step at -1. If we're currently inside a formatting
    # mark pair, skip parsing line breaks, which are not allowed inside paired
    # marks.
    if in_cite or in_bold or in_italic:
        handlers[-1] = lambda: parse_text(text)
    else:
        handlers[-1] = lambda: parse_breaks(text)
    # Choose the handler for the earliest found pair, or the default handler
    # at -1 if nothing was found.
    finds = [i for i in (next_cite, next_bold, next_italic) if i > -1]
    first = min(finds) if finds else -1
    return handlers[first]()


def find_pair(text: str, open_tag: str, close_tag: str) -> int:
    """
    Finds the beginning of a pair of formatting marks.
    """
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


def parse_citation(
    text: str,
    in_bold: bool = False,
    in_italic: bool = False,
) -> Spans:
    """
    Parses text into a citation span.
    """
    cite_open = text.find("[[")
    if cite_open > -1:
        cite_close = text.find("]]", cite_open + 2)
        # Since we searched for pairs from the beginning, there should be no
        # undetected pair formatting before this one, so move to the next
        # level of parsing
        spans_before = parse_breaks(text[:cite_open])
        # Continue parsing pair formatting after this one closes with all
        # three as valid choices
        spans_after = parse_paired_formatting(text[cite_close + 2 :])
        # Parse inner text and skip parsing for this format pair
        text_inner = text[cite_open + 2 : cite_close]
        # For citations specifically, try to split off a citation target.
        # If there's no citation target to split, use the same text as the
        # citation text and the target.
        inner_split = text_inner.split("|", 1)
        text_inner_actual, cite_target = inner_split[0], inner_split[-1]
        spans_inner = parse_paired_formatting(
            text_inner_actual, in_cite=True, in_bold=in_bold, in_italic=in_italic
        )
        citation = CitationSpan(spans_inner, cite_target)
        return [*spans_before, citation, *spans_after]
    # Should never happen
    return parse_breaks(text)


def parse_bold(
    text: str,
    in_cite: bool = False,
    in_italic: bool = False,
) -> Spans:
    """
    Parses text into a bold span.
    """
    bold_open = text.find("**")
    if bold_open > -1:
        bold_close = text.find("**", bold_open + 2)
        # Should be no formatting behind us
        spans_before = parse_breaks(text[:bold_open])
        # Freely parse formatting after us
        spans_after = parse_paired_formatting(text[bold_close + 2 :])
        # Parse inner text minus bold parsing
        text_inner = text[bold_open + 2 : bold_close]
        spans_inner = parse_paired_formatting(
            text_inner, in_cite=in_cite, in_bold=True, in_italic=in_italic
        )
        bold = BoldSpan(spans_inner)
        return [*spans_before, bold, *spans_after]
    # Should never happen
    return parse_italic(text)


def parse_italic(
    text: str,
    in_cite: bool = False,
    in_bold: bool = False,
) -> Spans:
    """
    Parses text into an italic span.
    """
    italic_open = text.find("//")
    if italic_open > -1:
        italic_close = text.find("//", italic_open + 2)
        # Should be no formatting behind us
        spans_before = parse_breaks(text[:italic_open])
        # Freely parse formatting after us
        spans_after = parse_paired_formatting(text[italic_close + 2 :])
        # Parse inner text minus italic parsing
        text_inner = text[italic_open + 2 : italic_close]
        spans_inner = parse_paired_formatting(
            text_inner, in_cite=in_cite, in_bold=in_bold, in_italic=True
        )
        italic = ItalicSpan(spans_inner)
        return [*spans_before, italic, *spans_after]
    # Should never happen
    return parse_breaks(text)


def parse_breaks(text: str) -> Spans:
    """
    Parses intra-paragraph line breaks.
    """
    # Parse empty text into nothing
    if not text:
        return []
    # Split on the line break mark appearing at the end of the line
    splits: Spans = list(map(TextSpan, text.split("\\\\\n")))
    # Put a LineBreak between each TextSpan
    spans: Spans = [
        splits[i // 2] if i % 2 == 0 else LineBreak()
        for i in range(0, 2 * len(splits) - 1)
    ]
    return spans


def parse_text(text: str) -> Spans:
    """
    Parses text with no remaining parseable marks.
    """
    if not text:
        return []
    return [TextSpan(text)]
