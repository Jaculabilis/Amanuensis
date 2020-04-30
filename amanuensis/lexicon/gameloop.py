"""
Submodule of functions for managing lexicon games during the core game
loop of writing and publishing articles.
"""
from collections import OrderedDict
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
	title: str) -> Tuple[List[str], List[str], List[str]]:
	"""
	Checks article constraints for the lexicon against a proposed
	draft title.
	"""
	infos: list = []
	warnings: list = []
	errors: list = []
	with lexicon.ctx.read('info') as info:
		# E: No title
		if not title:
			errors.append('Missing title')
			return infos, warnings, errors  # No point in further analysis
		# I: This article is new
		if title not in info:
			infos.append('New article')
		# I: This article is a phantom
		elif info[title].character is None:
			infos.append('Phantom article')
		# E: This article has already been written and addendums are disabled
		elif not lexicon.cfg.article.addendum.allowed:
			errors.append('Article already exists')
		# I: This article's index
		index = get_index_for_title(lexicon, title)
		infos.append(f'Article index: {index}')
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

	return infos, warnings, errors


def content_constraint_analysis(
	lexicon: LexiconModel,
	player: UserModel,
	cid: str,
	parsed) -> Tuple[List[str], List[str], List[str]]:
	"""
	Checks article constraints for the lexicon against the content of
	a draft
	"""
	infos: list = []
	warnings: list = []
	errors: list = []
	content_analysis: ConstraintAnalysis = (
		parsed.render(ConstraintAnalysis(lexicon)))
	with lexicon.ctx.read('info') as info:
		# I: Word count
		infos.append(f'Word count: {content_analysis.word_count}')
		# E: Self-citation when forbidden
		for citation in content_analysis.citations:
			citation_info = info.get(citation)
			if (citation_info and citation_info.character == cid
			and not lexicon.cfg.article.citation.allow_self):
				errors.append(f'Cited your own article: {citation}')
		# W: A new citation matches a character's name
			if not citation_info:
				for char in lexicon.cfg.character.values():
					if len(char.name) > 10 and citation == char.name:
						warnings.append(f'"{citation}" is the name of a '
							' character. Are you sure you want to do that?')
		# A new citation would create more articles than can be written
		pass  # TODO
		# E: Not enough extant citations
		citation_cfg = lexicon.cfg.article.citation
		extant_count = len(set([
			c for c in content_analysis.citations
			if c in info and info[c].character]))
		if (citation_cfg.min_extant is not None
		and extant_count < citation_cfg.min_extant):
			errors.append('Not enough extant articles cited '
				f'({extant_count}/{citation_cfg.min_extant})')
		# E: Too many extant citations
		if (citation_cfg.max_extant is not None
		and extant_count > citation_cfg.max_extant):
			errors.append('Too many extant articles cited '
				f'({extant_count}/{citation_cfg.max_extant})')
		# E: Not enough phantom citations
		phantom_count = len(set([
			c for c in content_analysis.citations
			if c not in info or not info[c].character]))
		if (citation_cfg.min_phantom is not None
		and phantom_count < citation_cfg.min_phantom):
			errors.append('Not enough phantom articles cited '
				f'({phantom_count}/{citation_cfg.min_phantom})')
		# E: Too many phantom citations
		if (citation_cfg.max_phantom is not None
		and phantom_count > citation_cfg.max_phantom):
			errors.append('Too many phantom articles cited '
				f'({phantom_count}/{citation_cfg.max_phantom})')
		# E: Not enough total citations
		total_count = len(set(content_analysis.citations))
		if (citation_cfg.min_total is not None
		and total_count < citation_cfg.min_total):
			errors.append('Not enough articles cited '
				f'({total_count}/{citation_cfg.min_total})')
		# E: Too many total citations
		if (citation_cfg.max_total is not None
		and total_count > citation_cfg.max_total):
			errors.append('Too many articles cited '
				f'({total_count}/{citation_cfg.max_total})')
		# E: Not enough characters' articles cited
		char_count = len(set([
			info[c].character
			for c in content_analysis.citations
			if c in info and info[c].character]))
		if (citation_cfg.min_chars is not None
		and char_count < citation_cfg.min_chars):
			errors.append('Not enough characters cited '
				f'({char_count}/{citation_cfg.min_chars})')
		# E: Too many characters' articles cited
		if (citation_cfg.max_chars is not None
		and char_count > citation_cfg.max_chars):
			errors.append('Too many characters cited '
				f'({char_count}/{citation_cfg.max_chars})')
		# E: Exceeded hard word limit
		if (lexicon.cfg.article.word_limit.hard is not None
			and content_analysis.word_count > lexicon.cfg.article.word_limit.hard):
			errors.append('Exceeded maximum word count '
				f'({lexicon.cfg.article.word_limit.hard})')
		# W: Exceeded soft word limit
		elif (lexicon.cfg.article.word_limit.soft is not None
			and content_analysis.word_count > lexicon.cfg.article.word_limit.soft):
			warnings.append('Exceeded suggested maximum word count '
				f'({lexicon.cfg.article.word_limit.soft})')
		# W: Missing signature
		if content_analysis.signatures < 1:
			warnings.append('Missing signature')
		# W: Multiple signatures
		if content_analysis.signatures > 1:
			warnings.append('Multiple signatures')

	return infos, warnings, errors


def index_match(index, title) -> bool:
	if index.type == 'char':
		return titlesort(title)[0].upper() in index.pattern.upper()
	if index.type == 'prefix':
		return title.startswith(index.pattern)
	if index.type == 'etc':
		return True
	raise ValueError(f'Unknown index type: "{index.type}"')


def get_index_for_title(lexicon: LexiconModel, title: str):
	"""
	Returns the index pattern for the given title.
	"""
	index_specs = lexicon.cfg.article.index.list
	index_by_pri: dict = {}
	for index in index_specs:
		if index.pri not in index_by_pri:
			index_by_pri[index.pri] = []
		index_by_pri[index.pri].append(index)
	index_eval_order = [
		index
		for pri in sorted(index_by_pri.keys(), reverse=True)
		for index in index_by_pri[pri]]
	for index in index_eval_order:
		if index_match(index, title):
			return index.pattern
	return "&c"


def sort_by_index_spec(articles, index_specs, key=None):
	"""
	Sorts a list under the appropriate index in the given index
	specification list. If the list is not a list of titles, the key
	function should map the contents to the indexable strings.
	"""
	if key is None:
		def key(k):
			return k
	# Determine the index evaluation order vs list order
	index_by_pri = {}
	index_list_order = []
	for index in index_specs:
		if index.pri not in index_by_pri:
			index_by_pri[index.pri] = []
		index_by_pri[index.pri].append(index)
		index_list_order.append(index)
	index_eval_order = [
		index
		for pri in sorted(index_by_pri.keys(), reverse=True)
		for index in index_by_pri[pri]]
	articles_titlesorted = sorted(
		articles,
		key=lambda a: titlesort(key(a)))
	indexed = OrderedDict()
	for index in index_list_order:
		indexed[index.pattern] = []
	for article in articles_titlesorted:
		for index in index_eval_order:
			if index_match(index, key(article)):
				indexed[index.pattern].append(article)
				break
	return indexed


def attempt_publish(lexicon: LexiconModel) -> bool:
	"""
	If the lexicon's publsh policy allows the current set of approved
	articles to be published, publish them and rebuild all pages.
	"""
	# Load all drafts
	draft_ctx = lexicon.ctx.draft
	drafts = {}
	for draft_fn in draft_ctx.ls():
		with draft_ctx.read(draft_fn) as draft_obj:
			drafts[draft_fn] = draft_obj

	# Check for whether the current turn can be published according to current
	# publish policy
	characters = [
		cid for cid, char in lexicon.cfg.character.items() if char.player]
	has_approved = {cid: 0 for cid in characters}
	has_ready = {cid: 0 for cid in characters}
	for draft in drafts.values():
		if draft.status.approved:
			has_approved[draft.character] = 1
		elif draft.status.ready:
			has_ready[draft.character] = 1
	# If quorum isn't defined, require all characters to have an article
	quorum = lexicon.cfg.publish.quorum or len(characters)
	if sum(has_approved.values()) < quorum:
		lexicon.log(f'Publish failed: no quorum')
		return False
	# If articles are up for review, check if this blocks publish
	if lexicon.cfg.publish.block_on_ready and any(has_ready.values()):
		lexicon.log(f'Publish failed: articles in review')
		return False

	# Get the approved drafts to publish
	to_publish = [
		draft_fn for draft_fn, draft in drafts.items()
		if draft.status.approved]

	# Publish new articles
	publish_drafts(lexicon, to_publish)

	# Rebuild all pages
	rebuild_pages(lexicon)

	return True


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
				dest.turn = lexicon.cfg.turn.current
		draft_ctx.delete(filename)
	# Increment the turn
	lexicon.log(f'Published turn {lexicon.cfg.turn.current}')
	with lexicon.ctx.edit_config() as cfg:
		cfg.turn.current += 1


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
