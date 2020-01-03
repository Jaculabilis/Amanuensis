# Standard library imports
from argparse import ArgumentParser as AP
from functools import wraps

#
# The cli module must not import other parts of the application at the module
# level. This is because most other modules depend on the config module. The
# config module may depend on __main__'s commandline parsing to locate config
# files, and __main__'s commandline parsing requires importing (but not
# executing) the functions in the cli module. Thus, cli functions must only
# import the config module inside the various command methods, which are only
# run after commandline parsing has already occurred.
#

#
# These function wrappers are used to make the command_* methods accept an
# ArgumentParser as a parameter, which it then configures with the given
# argument and returns. This way, we can configure each command's subparser
# in this module without having to write a separate function to configure it.
#
def add_argument(*args, **kwargs):
	"""Passes the given args and kwargs to subparser.add_argument"""
	def argument_adder(command):
		second_layer = command.__dict__.get('wrapper', False)
		@wraps(command)
		def augmented_command(cmd_args):
			if type(cmd_args) is AP:
				cmd_args.add_argument(*args, **kwargs)
			if type(cmd_args) is not AP or second_layer:
				command(cmd_args)
		augmented_command.__dict__['wrapper'] = True
		return augmented_command
	return argument_adder

def no_argument(command):
	"""Noops for subparsers"""
	@wraps(command)
	def augmented_command(cmd_args):
		if type(cmd_args) is not AP:
			command(cmd_args)
	return augmented_command


@add_argument("--update", action="store_true", help="Refresh an existing config directory")
def command_init(args):
	"""Initialize an Amanuensis config directory at the directory given by
	 --config-dir"""
	from collections import OrderedDict
	import fcntl
	import json
	import os
	import pkg_resources

	cfd = args.config_dir
	# Create the directory if it doesn't exist.
	if not os.path.isdir(cfd):
		os.mkdir(cfd)
	# The directory should be empty if we're not updating an existing one.
	if len(os.listdir(cfd)) > 0 and not args.update:
		print("Directory {} is not empty".format(cfd))
		return -1

	# Update or create global config.
	def_cfg = pkg_resources.resource_stream(__name__, "resources/default_config.json")
	if args.update and os.path.isfile(os.path.join(cfd, "config.json")):
		with open(os.path.join(cfd, "config.json"), 'r+', encoding='utf8') as cfg_file:
			fcntl.lockf(cfg_file, fcntl.LOCK_EX)
			old_cfg = json.load(cfg_file, object_pairs_hook=OrderedDict)
			new_cfg = json.load(def_cfg, object_pairs_hook=OrderedDict)
			merged = {}
			for key in new_cfg:
				merged[key] = old_cfg[key] if key in old_cfg else new_cfg[key]
				if key not in old_cfg:
					print("Added key '{}' to config".format(key))
			for key in old_cfg:
				if key not in new_cfg:
					print("Config contains unknown key '{}'".format(key))
					merged[key] = old_cfg[key]
			cfg_file.seek(0)
			json.dump(merged, cfg_file, allow_nan=False, indent='\t')
			cfg_file.truncate()
			fcntl.lockf(cfg_file, fcntl.LOCK_UN)
	else:
		with open(os.path.join(cfd, "config.json"), 'wb') as f:
			f.write(def_cfg.read())
	# Ensure pidfile exists.
	if not os.path.isfile(os.path.join(cfd, "pid")):
		with open(os.path.join(cfd, "pid"), 'w') as f:
			f.write(str(os.getpid()))
	# Ensure subdirs exist.
	if not os.path.isdir(os.path.join(cfd, "lexicon")):
		os.mkdir(os.path.join(cfd, "lexicon"))
	if not os.path.isdir(os.path.join(cfd, "user")):
		os.mkdir(os.path.join(cfd, "user"))

@add_argument("-a", "--address", default="127.0.0.1")
@add_argument("-p", "--port", default="5000")
def command_run(args):
	"""Runs the default Flask development server"""
	from app import app
	app.run(host=args.address, port=args.port)

@add_argument("--foo", action="store_true")
def command_dump(args):
	"""Dumps the global config or the config for the given lexicon"""
	import json
	import config
	print(json.dumps(config.GLOBAL_CONFIG, indent=2))

