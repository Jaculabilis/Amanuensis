from flask import Blueprint, render_template, g
from flask.helpers import url_for
from flask_login import current_user
from werkzeug.utils import redirect

from amanuensis.backend import postq
from amanuensis.db import Post
from amanuensis.parser import RenderableVisitor, parse_raw_markdown
from amanuensis.parser.core import *
from amanuensis.server.helpers import (
    lexicon_param,
    player_required,
    current_lexicon,
    current_membership,
)

from .forms import CreatePostForm


bp = Blueprint("posts", __name__, url_prefix="/posts", template_folder=".")


class PostFormatter(RenderableVisitor):
    """Parses stylistic markdown into HTML without links."""

    def TextSpan(self, span: TextSpan):
        return span.innertext

    def LineBreak(self, span: LineBreak):
        return "<br>"

    def ParsedArticle(self, span: ParsedArticle):
        return "\n".join(span.recurse(self))

    def BodyParagraph(self, span: BodyParagraph):
        return f'<p>{"".join(span.recurse(self))}</p>'

    def SignatureParagraph(self, span: SignatureParagraph):
        return (
            '<hr><span class="signature"><p>'
            f'{"".join(span.recurse(self))}'
            "</p></span>"
        )

    def BoldSpan(self, span: BoldSpan):
        return f'<b>{"".join(span.recurse(self))}</b>'

    def ItalicSpan(self, span: ItalicSpan):
        return f'<i>{"".join(span.recurse(self))}</i>'

    def CitationSpan(self, span: CitationSpan):
        return "".join(span.recurse(self))


def render_post_body(post: Post) -> str:
    """Parse and render the body of a post into post-safe HTML."""
    renderable: ParsedArticle = parse_raw_markdown(post.body)
    rendered: str = renderable.render(PostFormatter())
    return rendered


@bp.get("/")
@lexicon_param
@player_required
def list(lexicon_name):
    form = CreatePostForm()
    new_posts, old_posts = postq.get_posts_for_membership(g.db, current_membership.id)
    return render_template(
        "posts.jinja",
        lexicon_name=lexicon_name,
        form=form,
        render_post_body=render_post_body,
        new_posts=new_posts,
        old_posts=old_posts,
    )


@bp.post("/")
@lexicon_param
@player_required
def create(lexicon_name):
    form = CreatePostForm()
    if form.validate():
        # Data is valid
        postq.create(g.db, current_lexicon.id, current_user.id, form.body.data)
        return redirect(url_for("lexicon.posts.list", lexicon_name=lexicon_name))

    else:
        # POST received invalid data
        return render_template(
            "posts.jinja",
            lexicon_name=lexicon_name,
            form=form,
            render_post_body=render_post_body,
        )
