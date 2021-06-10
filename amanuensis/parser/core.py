"""
Internal module encapsulating the core types for parsing Lexipython
markdown. Parsed articles are represented as a hierarchy of tokens,
which can be operated on by a visitor defining functions that hook off
of the different token types.
"""

from typing import Callable, Any, Sequence

from .helpers import normalize_title


RenderHook = Callable[["Renderable"], Any]
Spans = Sequence["Renderable"]


class Renderable:
    """
    Base class for parsed markdown. Provides the `render()` method for
    visiting the token tree.
    """

    def render(self: "Renderable", renderer: "RenderableVisitor"):
        """
        Execute the apppropriate visitor method on this Renderable.
        Visitors implement hooks by declaring methods whose names are
        the name of a Renderable class.
        """
        hook: RenderHook = getattr(renderer, type(self).__name__, None)
        if hook:
            return hook(self)
        return None


class TextSpan(Renderable):
    """A length of text."""

    def __init__(self, innertext: str):
        self.innertext = innertext

    def __repr__(self):
        return f"<{self.innertext}>"


class LineBreak(Renderable):
    """A line break within a paragraph."""

    def __repr__(self):
        return "<break>"


class SpanContainer(Renderable):
    """A formatting element that wraps some amount of text."""

    def __init__(self, spans: Spans):
        self.spans: Spans = spans

    def __repr__(self):
        return (
            f"<{type(self).__name__} "
            + f'{" ".join([repr(span) for span in self.spans])}>'
        )

    def recurse(self, renderer: "RenderableVisitor"):
        return [child.render(renderer) for child in self.spans]


class ParsedArticle(SpanContainer):
    """Token tree root node, containing some number of paragraph tokens."""


class BodyParagraph(SpanContainer):
    """A normal paragraph."""


class SignatureParagraph(SpanContainer):
    """A paragraph preceded by a signature mark."""


class BoldSpan(SpanContainer):
    """A span of text inside bold marks."""


class ItalicSpan(SpanContainer):
    """A span of text inside italic marks."""


class CitationSpan(SpanContainer):
    """A citation to another article."""

    def __init__(self, spans: Spans, cite_target: str):
        super().__init__(spans)
        # Normalize citation target on parse, since we don't want
        # abnormal title strings lying around causing trouble.
        self.cite_target: str = normalize_title(cite_target)

    def __repr__(self) -> str:
        return (
            f'{{{" ".join([repr(span) for span in self.spans])}'
            + f":{self.cite_target}}}"
        )


class RenderableVisitor:
    """
    Default implementation of the visitor pattern. Executes once on
    each token in the tree and returns itself.
    """

    def TextSpan(self, span: TextSpan):
        return self

    def LineBreak(self, span: LineBreak):
        return self

    def ParsedArticle(self, span: ParsedArticle):
        span.recurse(self)
        return self

    def BodyParagraph(self, span: BodyParagraph):
        span.recurse(self)
        return self

    def SignatureParagraph(self, span: SignatureParagraph):
        span.recurse(self)
        return self

    def BoldSpan(self, span: BoldSpan):
        span.recurse(self)
        return self

    def ItalicSpan(self, span: ItalicSpan):
        span.recurse(self)
        return self

    def CitationSpan(self, span: CitationSpan):
        span.recurse(self)
        return self
