# Amanuensis

_amanuensis, n. One who copies or writes from the dictation of another._ -OED

**Amanuensis** is a web application using Flask on top of Python 3 for managing games of Lexicon, the worldbuilding RPG.

### Lexicon in short

Lexicon is a role-playing game in which players take on the role of scholars. These scholars are collaborating on the construction of an encyclopedia describing some fantastic world or historical period. Each turn, players submit articles on some particular topic, citing other articles within the burgeoning encyclopedia. This process is complicated by three factors. First, some of the articles being cited will not exist at the time they are cited. Second, players may not cite themselves. Third, players may not contradict anything another player has said.

For more information on the game of Lexicon, see the [Lexicon README](README.LEXICON.md).

### Amanuensis in short

Amanuensis is the successor to [Lexipython](https://github.com/Jaculabilis/Lexipython). Lexipython provides scripting to build lexicons from markdown files, but otherwise provides no solution for article intake or game hosting. The goal of Amanuensis is to provide centralized workflows for the entire game of Lexicon, from creating the game to writing articles for each turn to compiling the final product. Eventually, Amanuensis will be able to dump static files from a Lexicon game, at which point Lexipython will be discontinued.

For technical information on Amanuensis, see the [technical README](README.AMANUENSIS.md).

## Running Amanuensis

Amanuensis is currently developed with Python 3.6 on Ubuntu. Some file locking code uses Linux-specific functionality. There are no plans at present to make the Amanuensis server run on Windows.

Most commands require that the `--config-dir` commandline argument point to a valid config directory. Use `amanuensis init` to create a config directory at the given location instead of loading one. The config directory contains private information, so it shouldn't be publicly visible. If an update to Amanuensis causes your config directory to be missing a required config value, run `amanuensis init --update`.

Amanuensis is installable as a package within a virtual environment using `pip install -e .` and runnable using `python -m amanuensis`. Currently, `amanuensis run` runs the default Flask development server, which is unsuited for visibility to the public Internet. If you run it, it should only be accessible on a secure local network. Before you can run the server, you will need to `amanuensis generate-secret`.