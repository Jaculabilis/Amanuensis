import os

from cli.helpers import (
	add_argument, no_argument,
	config_get, config_set, CONFIG_GET_ROOT_VALUE)

@add_argument(
	"--refresh", action="store_true",
	help="Refresh an existing config directory")
def command_init(args):
	"""
	Initialize a config directory at --config-dir

	A clean config directory will contain a config.json, a
	pidfile, a lexicon config directory, and a user config
	directory.

	Refreshing an existing directory will add keys to the global config that
	are present in the default configs. Users and lexicons that are missing
	from the indexes will be deleted, and stale index entries will be removed.
	"""
	# Module imports
	from config.init import create_config_dir

	# Verify arguments
	if args.refresh and not os.path.isdir(args.config_dir):
		print("Error: couldn't find directory '{}'".format(args.config_dir))

	# Internal call
	create_config_dir(args.config_dir, args.refresh)


@no_argument
def command_generate_secret(args):
	"""
	Generate a Flask secret key

	The Flask server will not run unless a secret key has
	been generated.
	"""
	import os

	import config

	secret_key = os.urandom(32)
	with config.json_rw("config.json") as cfg:
		cfg['secret_key'] = secret_key.hex()
	config.logger.info("Regenerated Flask secret key")


@add_argument("-a", "--address", default="127.0.0.1")
@add_argument("-p", "--port", default="5000")
def command_run(args):
	"""
	Run the default Flask server
	
	The default Flask server is not secure, and should
	only be used for development.
	"""
	import server
	import config

	if config.get("secret_key") is None:
		config.logger.error("Can't run server without a secret_key. Run generate-secret first")
		return -1
	server.app.run(host=args.address, port=args.port)


@add_argument("--get", metavar="PATHSPEC", dest="get",
	nargs="?", const=CONFIG_GET_ROOT_VALUE, help="Get the value of a config key")
@add_argument("--set", metavar=("PATHSPEC", "VALUE"), dest="set",
	nargs=2, help="Set the value of a config key")
def command_config(args):
	"""
	Interact with the global config

	PATHSPEC is a path into the config object formatted as
	a dot-separated sequence of keys.
	"""
	import json
	import config

	if args.get and args.set:
		config.logger.error("Specify one of --get and --set")
		return -1

	if args.get:
		with config.json_ro('config.json') as cfg:
			config_get(cfg, args.get)

	if args.set:
		with config.json_rw('config.json') as cfg:
			config_set("config", cfg, args.set)
