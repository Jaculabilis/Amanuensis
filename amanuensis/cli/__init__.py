#
# The cli module must not import other parts of the application at the module
# level. This is because most other modules depend on the config module. The
# config module may depend on __main__'s commandline parsing to locate config
# files, and __main__'s commandline parsing requires importing (but not
# executing) the functions in the cli module. Thus, cli functions must only
# import the config module inside the various command methods, which are only
# run after commandline parsing has already occurred.
#

def server_commands(commands={}):
	if commands: return commands
	import cli.server
	for name, func in vars(cli.server).items():
		if name.startswith("command_"):
			name = name[8:].replace("_", "-")
			commands[name] = func
	return commands

def lexicon_commands(commands={}):
	if commands: return commands
	import cli.lexicon
	for name, func in vars(cli.lexicon).items():
		if name.startswith("command_"):
			name = name[8:].replace("_", "-")
			commands["lexicon-" + name] = func
	return commands

def user_commands(commands={}):
	if commands: return commands
	import cli.user
	for name, func in vars(cli.user).items():
		if name.startswith("command_"):
			name = name[8:].replace("_", "-")
			commands["user-" + name] = func
	return commands

def get_commands():
	return {**server_commands(), **lexicon_commands(), **user_commands()}

def cmd_desc(func):
	return ((func.__doc__ or "").strip() or '\n').splitlines()[0]

def describe_commands():
	longest = max(map(len, server_commands().keys()))
	server_desc = "General commands:\n{}\n".format("\n".join([
		" {1:<{0}} : {2}".format(longest, name, cmd_desc(func))
		for name, func in server_commands().items()
	]))

	longest = max(map(len, lexicon_commands().keys()))
	lexicon_desc = "Lexicon commands:\n{}\n".format("\n".join([
		" {1:<{0}} : {2}".format(longest, name, cmd_desc(func))
		for name, func in lexicon_commands().items()
	]))

	longest = max(map(len, user_commands().keys()))
	user_desc = "User commands:\n{}\n".format("\n".join([
		" {1:<{0}} : {2}".format(longest, name, cmd_desc(func))
		for name, func in user_commands().items()
	]))

	return "\n".join([server_desc, lexicon_desc, user_desc])
