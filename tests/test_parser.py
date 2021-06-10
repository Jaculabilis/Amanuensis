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
    SpanContainer,
    RenderableVisitor,
    Spans,
)
from amanuensis.parser.helpers import normalize_title, filesafe_title, titlesort
from amanuensis.parser.parsing import (
    parse_breaks,
    parse_paired_formatting,
    parse_paragraph,
    parse_raw_markdown,
)


def assert_types(spans: Spans, types: Sequence, loc=None):
    """
    Asserts that  a span list has the types specified.
    Each element in `types` should be either a span type or a list. The first
    element of the list is the container type and the remaining elements are the
    content types.
    """
    assert len(spans) == len(
        types
    ), f"Unexpected type sequence length at loc {loc if loc else 'root'}"
    i = -1
    for span, span_type in zip(spans, types):
        i += 1
        i_loc = f"{loc}.{i}" if loc else f"{i}"
        if isinstance(span_type, list):
            assert isinstance(
                span, SpanContainer
            ), f"Expected a span container at loc {i_loc}"
            assert (
                len(span.spans) == len(span_type) - 1
            ), f"Unexpected container size at loc {i_loc}"
            assert isinstance(
                span, span_type[0]
            ), f"Unexpected container type at loc {i_loc}"
            assert_types(span.spans, span_type[1:], loc=i_loc)
        else:
            assert isinstance(span, Renderable), f"Expected a span at loc {i_loc}"
            assert isinstance(span, span_type), f"Unexpected span type at loc {i_loc}"


def assert_text(spans: Spans, texts: Sequence, loc=None):
    """
    Asserts that a span list has the inner text structure specified.
    Each element in `texts` should be either a string or a list of the same.
    """
    assert len(spans) == len(
        texts
    ), f"Unexpected text sequence length at loc {loc if loc else 'root'}"
    i = -1
    for span, text in zip(spans, texts):
        i += 1
        i_loc = f"{loc}.{i}" if loc else f"{i}"
        if isinstance(text, str):
            assert isinstance(span, TextSpan), f"Expected a text span at loc {i_loc}"
            assert span.innertext == text, f"Unexpected text at loc {i_loc}"
        elif isinstance(text, list):
            assert isinstance(
                span, SpanContainer
            ), f"Expected a span container at loc {i_loc}"
            assert_text(span.spans, text, loc=i_loc)
        else:
            assert isinstance(span, LineBreak), f"Expected a line break at loc {i_loc}"


def test_parse_breaks():
    """Test parsing for intra-pragraph line break"""
    text: str
    spans: Spans

    # Only having a line break does nothing
    text = "One\nTwo"
    spans: Spans = parse_breaks(text)
    assert_types(spans, [TextSpan])
    assert_text(spans, [text])

    # Having the mark causes the text to be split across it
    text = r"One\\" + "\nTwo"
    spans: Spans = parse_breaks(text)
    assert_types(spans, [TextSpan, LineBreak, TextSpan])
    assert_text(spans, ["One", None, "Two"])

    # Multiple lines can be broken
    text = r"One\\" + "\n" + r"Two\\" + "\nThree"
    spans: Spans = parse_breaks(text)
    assert_types(spans, [TextSpan, LineBreak, TextSpan, LineBreak, TextSpan])
    assert_text(spans, ["One", None, "Two", None, "Three"])

    # The mark must be at the end of the line
    text = r"One\\ " + "\nTwo"
    spans: Spans = parse_breaks(text)
    assert_types(spans, (TextSpan,))
    assert_text(spans, [text])


def test_parse_pairs_single():
    """Test parsing for bold and italic marks"""
    text: str
    spans: Spans

    # Empty pair marks should parse
    text = "****"
    spans = parse_paired_formatting(text)
    assert_types(spans, [[BoldSpan]])

    text = "////"
    spans = parse_paired_formatting(text)
    assert_types(spans, [[ItalicSpan]])

    # Pair marks with text inside should parse
    text = "**hello**"
    spans = parse_paired_formatting(text)
    assert_types(spans, [[BoldSpan, TextSpan]])
    assert_text(spans, [["hello"]])

    text = "//hello//"
    spans = parse_paired_formatting(text)
    assert_types(spans, [[ItalicSpan, TextSpan]])
    assert_text(spans, [["hello"]])

    # Text outside of pair marks should parse on the same level
    text = "**hello** world"
    spans = parse_paired_formatting(text)
    assert_types(spans, [[BoldSpan, TextSpan], TextSpan])
    assert_text(spans, [["hello"], " world"])

    text = "//hello// world"
    spans = parse_paired_formatting(text)
    assert_types(spans, [[ItalicSpan, TextSpan], TextSpan])
    assert_text(spans, [["hello"], " world"])

    # Text before, between, and after pair marks should parse
    text = "In the **beginning** was //the// Word"
    spans = parse_paired_formatting(text)
    assert_types(
        spans,
        [TextSpan, [BoldSpan, TextSpan], TextSpan, [ItalicSpan, TextSpan], TextSpan],
    )
    assert_text(spans, ["In the ", ["beginning"], " was ", ["the"], " Word"])


def test_parse_pairs_break():
    """Test pair marks with breaks"""
    text: str
    spans: Spans

    text = r"**glory\\" + "\nhammer**"
    spans = parse_paired_formatting(text)
    assert_types(spans, [[BoldSpan, TextSpan]])
    assert_text(spans, [["glory\\\\\nhammer"]])

    text = r"//glory\\" + "\nhammer//"
    spans = parse_paired_formatting(text)
    assert_types(spans, [[ItalicSpan, TextSpan]])
    assert_text(spans, [["glory\\\\\nhammer"]])

    text = r"**glory\\" + "\n**hammer**"
    spans = parse_paired_formatting(text)
    assert_types(spans, [[BoldSpan, TextSpan], TextSpan])
    assert_text(spans, [["glory\\\\\n"], "hammer**"])

    text = r"//glory\\" + "\n//hammer//"
    spans = parse_paired_formatting(text)
    assert_types(spans, [[ItalicSpan, TextSpan], TextSpan])
    assert_text(spans, [["glory\\\\\n"], "hammer//"])


def test_parse_pairs_nested():
    """Test parsing for nesting bold and italic"""
    text: str
    spans: Spans

    # Simple nested test cases
    text = "**//hello//**"
    spans = parse_paired_formatting(text)
    assert_types(spans, [[BoldSpan, [ItalicSpan, TextSpan]]])
    assert_text(spans, [[["hello"]]])

    text = "//**world**//"
    spans = parse_paired_formatting(text)
    assert_types(spans, [[ItalicSpan, [BoldSpan, TextSpan]]])
    assert_text(spans, [[["world"]]])

    # Overlap should only parse the first
    text = "**Hello//world**//"
    spans = parse_paired_formatting(text)
    assert_types(spans, [[BoldSpan, TextSpan], TextSpan])
    assert_text(spans, [["Hello//world"], "//"])


def test_normalize_title():
    """Test the title normalization used by the citation parser"""
    nt = normalize_title
    assert nt("hello") == "Hello"
    assert nt("  world  ") == "World"
    assert nt("Waiting for           Godot") == "Waiting for Godot"
    assert nt("lowercase letters") == "Lowercase letters"


def test_parse_citation_single():
    """Test parsing citations, which have internal formatting"""
    text: str
    spans: Spans

    # Simple test cases
    text = "[[hello]]"
    spans = parse_paired_formatting(text)
    assert_types(spans, [[CitationSpan, TextSpan]])
    assert_text(spans, [["hello"]])
    citation: CitationSpan = spans[0]
    assert citation.cite_target == "Hello"

    text = "[[hello|world]]"
    spans = parse_paired_formatting(text)
    assert_types(spans, [[CitationSpan, TextSpan]])
    assert_text(spans, [["hello"]])
    citation: CitationSpan = spans[0]
    assert citation.cite_target == "World"

    text = "[[hello||world]]"
    spans = parse_paired_formatting(text)
    assert_types(spans, [[CitationSpan, TextSpan]])
    assert_text(spans, [["hello"]])
    citation: CitationSpan = spans[0]
    assert citation.cite_target == "|world"

    text = "[[  hello  |  world  ]]"
    spans = parse_paired_formatting(text)
    assert_types(spans, [[CitationSpan, TextSpan]])
    assert_text(spans, [["  hello  "]])
    citation: CitationSpan = spans[0]
    assert citation.cite_target == "World"

    text = "[[faith|hope|love]]"
    spans = parse_paired_formatting(text)
    assert_types(spans, [[CitationSpan, TextSpan]])
    assert_text(spans, [["faith"]])
    citation: CitationSpan = spans[0]
    assert citation.cite_target == "Hope|love"

    text = "[[ [[|]] ]]"
    spans = parse_paired_formatting(text)
    assert_types(spans, [[CitationSpan, TextSpan], TextSpan])
    assert_text(spans, [[" [["], " ]]"])
    citation: CitationSpan = spans[0]
    assert citation.cite_target == ""


def test_parse_citation_break():
    """Test citations with breaks"""
    text: str
    spans: Spans

    text = "[[hello\\\\\nworld]]"
    spans = parse_paired_formatting(text)
    assert_types(spans, [[CitationSpan, TextSpan]])
    assert_text(spans, [["hello\\\\\nworld"]])
    citation: CitationSpan = spans[0]
    assert citation.cite_target == "Hello\\\\ world"

    text = "[[one|two\\\\\nthree]]"
    spans = parse_paired_formatting(text)
    assert_types(spans, [[CitationSpan, TextSpan]])
    assert_text(spans, [["one"]])
    citation: CitationSpan = spans[0]
    assert citation.cite_target == "Two\\\\ three"


def test_parse_citation_nested():
    """Test nesting with citations"""
    text: str
    spans: Spans

    text = "[[**hello world**]]"
    spans = parse_paired_formatting(text)
    assert_types(spans, [[CitationSpan, [BoldSpan, TextSpan]]])
    assert_text(spans, [[["hello world"]]])
    citation: CitationSpan = spans[0]
    assert citation.cite_target == "**hello world**"

    text = "[[**hello|world**]]"
    spans = parse_paired_formatting(text)
    assert_types(spans, [[CitationSpan, TextSpan]])
    assert_text(spans, [["**hello"]])
    citation: CitationSpan = spans[0]
    assert citation.cite_target == "World**"

    text = "**[[hello world]]**"
    spans = parse_paired_formatting(text)
    assert_types(spans, [[BoldSpan, [CitationSpan, TextSpan]]])
    assert_text(spans, [[["hello world"]]])
    citation: CitationSpan = spans[0].spans[0]
    assert citation.cite_target == "Hello world"

    text = "**[[hello world**]]"
    spans = parse_paired_formatting(text)
    assert_types(spans, [[BoldSpan, TextSpan], TextSpan])
    assert_text(spans, [["[[hello world"], "]]"])

    text = "[[**hello world]]**"
    spans = parse_paired_formatting(text)
    assert_types(spans, [[CitationSpan, TextSpan], TextSpan])
    assert_text(spans, [["**hello world"], "**"])
    citation: CitationSpan = spans[0]
    assert citation.cite_target == "**hello world"
