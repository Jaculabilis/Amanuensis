"""
Submodule of functions for managing lexicon games during the core game
loop of writing and publishing articles.
"""
from typing import Iterable, Any, List, Optional, Tuple

from amanuensis.config import ReadOnlyOrderedDict
from amanuensis.models import LexiconModel, UserModel
from amanuensis.parser import (
	parse_raw_markdown,
	GetCitations,
	HtmlRenderer,
	titlesort,
	filesafe_title,
	ConstraintAnalysis)


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


def get_draft(
	lexicon: LexiconModel,
	aid: str) -> Optional[ReadOnlyOrderedDict]:
	"""
	Loads an article from its id
	"""
	article_fn = None
	for filename in lexicon.ctx.draft.ls():
		if filename.endswith(f'{aid}.json'):
			article_fn = filename
			break
	if not article_fn:
		return None
	with lexicon.ctx.draft.read(article_fn) as article:
		return article


def title_constraint_analysis(
	lexicon: LexiconModel,
	player: UserModel,
	title: str) -> Tuple[List[str], List[str]]:
	"""
	Checks article constraints for the lexicon against a proposed
	draft title.
	"""
	warnings = []
	errors = []
	with lexicon.ctx.read('info') as info:
		# No title
		if not title:
			errors.append('Missing title')
			return warnings, errors  # No point in further analysis
		# The article does not sort under the player's assigned index
		pass
		# The article's title is new, but its index is full
		pass
		# The article's title is a phantom, but the player has cited it before
		info
		# Another player is writing an article with this title
		pass  # warning
		# Another player has an approved article with this title
		pass
		# An article with this title was already written and addendums are
		# disabled
		pass
		# An article with this title was already written and this player has
		# reached the maximum number of addendum articles
		pass
		# The article's title matches a character's name
		pass  # warning

	return warnings, errors


def content_constraint_analysis(
	lexicon: LexiconModel,
	player: UserModel,
	cid: str,
	parsed) -> Tuple[List[str], List[str], List[str]]:
	"""
	Checks article constraints for the lexicon against the content of
	a draft
	"""
	infos = []
	warnings = []
	errors = []
	character = lexicon.cfg.character.get(cid)
	content_analysis: ConstraintAnalysis = (
		parsed.render(ConstraintAnalysis(lexicon)))
	with lexicon.ctx.read('info') as info:
		infos.append(f'Word count: {content_analysis.word_count}')
		# Self-citation when forbidden
		pass
		# A new citation matches a character's name
		pass  # warning
		# A new citation would create more articles than can be written
		# Not enough extant citations
		# Too many extant citations
		# Not enough phantom citations
		# Too many phantom citations
		# Not enough total citations
		# Too many total citations
		# Not enough characters' articles cited
		# Too many characters' articles cited
		# Exceeded hard word limit
		if (lexicon.cfg.article.word_limit.hard is not None
			and content_analysis.word_count > lexicon.cfg.article.word_limit.hard):
			errors.append('Exceeded maximum word count '
				f'({lexicon.cfg.article.word_limit.hard})')
		# Exceeded soft word limit
		elif (lexicon.cfg.article.word_limit.soft is not None
			and content_analysis.word_count > lexicon.cfg.article.word_limit.soft):
			warnings.append('Exceeded suggested maximum word count '
				f'({lexicon.cfg.article.word_limit.soft})')
		# Missing signature
		if content_analysis.signatures < 1:
			warnings.append('Missing signature')
		# Multiple signatures
		if content_analysis.signatures > 1:
			warnings.append('Multiple signatures')
		# Signature altered from default
		pass  # warning

	return infos, warnings, errors


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
