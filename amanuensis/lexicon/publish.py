"""
The article writing workflow proceeds through the following states:

* Active: When player creates a draft, it is initialized with this state.
  Players can view and edit their active drafts. Admins can view all active
  drafts. Active drafts occupy an index slot in the lexicon, but the title is
  elided.

  Players can mark their active drafts as ready for publication, which
  transitions the draft to the Ready state. If publish.notify.editor_on_ready
  is true, the editor will be notified.

* Ready: Players can view but not edit their ready drafts. Editors and admins
  can view all ready drafts. The editor's session page lists all ready drafts
  for that lexicon. Ready drafts occupy an index slot with an elided title.

  A player can unready a ready draft, which transitions it to the Active state.

  The editor can approve a ready draft, which transitions it to the Locked
  state, or reject it, which transitions it to the Active state and includes a
  message from the editor to the player who owns it. If either
  publish.notify.player_on_reject or publish.notify.player_on_accept is true,
  the player will be notified in that case.

* Locked: Players can view but not edit their locked drafts. Editors and admins
  admins can view all locked drafts. The editor's session page lists all
  locked drafts for that lexicon. Locked drafts occupy an index slot with an
  elided title.

Turn publishing can be attempted by executing the lexicon-publish-turn command.
Automatic publishing is controlled by two settings: asap and deadlines.

* asap: If publish.asap is true, when the editor approves a draft, Amanuensis
  will check if each character has a locked draft. If so, publishing will be
  attempted immediately.

* deadlines: publish.deadlines should be a crontab-format time specification.
  This will be prepended to the publish command and inserted into the user
  crontab. The command uses --as-deadline to differentiate scheduled publish
  attempts from manual ones. If publish.deadlines is empty, no crontab entry
  will be used.

Whenever publishing is attempted, either internally via asap or externally via
invocation by command line or cron job, Amanuensis checks if every character in
the lexicon has a locked draft. If so, the turn is published. If not, publish
behavior follows two settings: quorum and block_on_ready.

* quorum: If publish.quorum is defined, then Amanuensis will check if there are
  at least $quorum number of locked articles. If there are, then turn
  publishing will proceed with just those articles. If there are not, but there
  are enough ready articles to make quorum and --as-deadline was specified, then
  the editor will be notified that they are blocking the turn. If there are not
  enough ready articles to make quorum and --as-deadline was specified, then
  players with characters without ready articles will be notified that they are
  blocking the turn.

* block_on_ready: If publish.block_on_ready is true, then turn publishing will
  fail if any character missing a locked article has a ready article. The
  editor will be notified that they are blocking the turn.

* --force can be specified to lexicon-publish-turn to skip both quorum and
  block_on_ready checks.
"""