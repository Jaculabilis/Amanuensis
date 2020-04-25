"""
Submodule of functions for managing lexicon games during the core game
loop of writing and publishing articles.
"""
from typing import Iterable, Any, List

from amanuensis.config import ReadOnlyOrderedDict
from amanuensis.models import LexiconModel
from amanuensis.parser import (
	parse_raw_markdown,
	GetCitations,
	HtmlRenderer,
	titlesort,
	filesafe_title)


def get_player_characters(
	lexicon: LexiconModel,
	uid: str) -> Iterable[ReadOnlyOrderedDict]:
	"""
	Returns each character in the lexicon owned by the given player
	"""
	for character in lexicon.cfg.character.values():
		if character.player == uid:
			yield character


def get_player_drafts(
	lexicon: LexiconModel,
	uid: str) -> Iterable[ReadOnlyOrderedDict]:
	"""
	Returns each draft in the lexicon by a character owned by the
	given player.
	"""
	characters = list(get_player_characters(lexicon, uid))
	drafts: List[Any] = []
	for filename in lexicon.ctx.draft.ls():
		for character in characters:
			if filename.startswith(character.cid):
				drafts.append(filename)
				break
	for i in range(len(drafts)):
		with lexicon.ctx.draft.read(drafts[i]) as draft:
			drafts[i] = draft
	return drafts


def attempt_publish(lexicon: LexiconModel) -> None:
	"""
	If the lexicon's publsh policy allows the current set of approved
	articles to be published, publish them and rebuild all pages.
	"""
	# TODO Check against lexicon publish policy

	# Get the approved drafts to publish
	draft_ctx = lexicon.ctx.draft
	to_publish = []
	for draft_fn in draft_ctx.ls():
		with draft_ctx.read(draft_fn) as draft:
			if draft.status.approved:
				to_publish.append(draft_fn)

	# Publish new articles
	publish_drafts(lexicon, to_publish)

	# Rebuild all pages
	rebuild_pages(lexicon)


def publish_drafts(lexicon: LexiconModel, filenames: Iterable[str]) -> None:
	"""
	Moves the given list of drafts to the article source directory
	"""
	# Move the drafts to src
	draft_ctx = lexicon.ctx.draft
	src_ctx = lexicon.ctx.src
	for filename in filenames:
		with draft_ctx.read(filename) as source:
			with src_ctx.edit(filename, create=True) as dest:
				dest.update(source)
		draft_ctx.delete(filename)


def rebuild_pages(lexicon: LexiconModel) -> None:
	"""
	Rebuilds all cached html
	"""
	src_ctx = lexicon.ctx.src
	article: Any = None  # typing workaround

	# Load all articles in the source directory and rebuild their renderable trees
	article_model_by_title = {}
	article_renderable_by_title = {}
	for filename in src_ctx.ls():
		with src_ctx.read(filename) as article:
			article_model_by_title[article.title] = article
			article_renderable_by_title[article.title] = (
				parse_raw_markdown(article.contents))

	# Get all citations
	citations_by_title = {}
	for title, article in article_renderable_by_title.items():
		citations_by_title[title] = sorted(
			set(article.render(GetCitations())), key=titlesort)

	# Get the written and phantom lists from the citation map
	written_titles = list(citations_by_title.keys())
	phantom_titles = []
	for citations in citations_by_title.values():
		for title in citations:
			if title not in written_titles and title not in phantom_titles:
				phantom_titles.append(title)

	# Build the citation map and save it to the info cache
	with lexicon.ctx.edit('info', create=True) as info:
		for title in info.keys():
			if title not in written_titles and title not in phantom_titles:
				del info[title]
		for title in written_titles:
			info[title] = {
				'citations': citations_by_title[title],
				'character': article_model_by_title[title].character
			}
		for title in phantom_titles:
			info[title] = {
				'citations': [],
				'character': None,
			}

	# Render article HTML and save to article cache
	for title, article in article_renderable_by_title.items():
		html = article.render(HtmlRenderer(lexicon.cfg.name, written_titles))
		filename = filesafe_title(title)
		with lexicon.ctx.article.edit(filename, create=True) as f:
			f['title'] = title
			f['html'] = html
			f['cites'] = citations_by_title[title]
			f['citedby'] = [
				citer for citer, citations
				in citations_by_title.items()
				if title in citations]

	for title in phantom_titles:
		filename = filesafe_title(title)
		with lexicon.ctx.article.edit(filename, create=True) as f:
			f['title'] = title
			f['html'] = ""
			f['cites'] = []
			f['citedby'] = [
				citer for citer, citations
				in citations_by_title.items()
				if title in citations]
