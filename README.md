# Amanuensis

_amanuensis, n. One who copies or writes from the dictation of another._ -OED

**Amanuensis** is a web application using Flask on top of Python 3 for managing games of Lexicon, the worldbuilding RPG.

### Lexicon in short

Lexicon is a role-playing game in which players take on the role of scholars. These scholars are collaborating on the construction of an encyclopedia describing some fantastic world or historical period. Each turn, players submit articles on some particular topic, citing other articles within the burgeoning encyclopedia. This process is complicated by three factors. First, some of the articles being cited will not exist at the time they are cited. Second, players may not cite themselves. Third, players may not contradict anything another player has said.

For more information on Lexicon, check back later when I write a readme about it.

### Amanuensis in short

Amanuensis is the successor to [Lexipython](https://github.com/Jaculabilis/Lexipython). Lexipython provides scripting to build lexicons from markdown files, but otherwise provides no solution for article intake or game hosting. The goal of Amanuensis is to provide centralized workflows for the entire game of Lexicon, from creating the game to writing articles for each turn to publishing the final product.

## Running Amanuensis

Amanuensis is currently developed with Python 3.6 on Ubuntu. Some I/O code uses the `fcntl` library, which is not supported on Windows; there are no plans at present to make Amanuensis run on Windows. A future version may provide simple scripting capabilities that work on Windows, but don't count on it and try Lexipython instead.

Most commands require that the `--config-dir` commandline argument point to a valid config directory. Use `amanuensis init` to create a config directory at the given location instead of loading one. The config directory contains private information, so it shouldn't be publicly visible. If an update to Amanuensis causes your config directory to be missing a required config value, run `amanuensis init --update`.

Currently, Amanuensis is only run using the default Flask development server, which is unsuited for visibility to the public Internet. If you run it, it should only be accessible on a secure local network. Before you can run the server, you will need to `amanuensis generate-secret`. Run the server with `amanuensis run`.