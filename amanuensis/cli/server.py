from cli.helpers import add_argument, no_argument

CONFIG_GET_ROOT_VALUE = object()

@add_argument("--update", action="store_true", help="Refresh an existing config directory")
def command_init(args):
	"""Initialize a config directory at the directory given by --config-dir"""
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
	if not os.path.isfile(os.path.join(cfd, 'user', 'index.json')):
		with open(os.path.join(cfd, 'user', 'index.json'), 'w') as f:
			json.dump({}, f)

@no_argument
def command_generate_secret(args):
	"""Generate a secret key for Flask"""
	import os

	import config

	secret_key = os.urandom(32)
	with config.json_rw("config.json") as cfg:
		cfg['secret_key'] = secret_key.hex()
	config.logger.info("Regenerated Flask secret key")

@add_argument("-a", "--address", default="127.0.0.1")
@add_argument("-p", "--port", default="5000")
def command_run(args):
	"""Run the default Flask server"""
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
	"""Interact with the global config"""
	import json
	import config

	if args.get and args.set:
		config.logger.error("Specify one of --get and --set")
		return -1

	if args.get:
		if args.get is CONFIG_GET_ROOT_VALUE:
			path = []
		else:
			path = args.get.split(".")
		with config.json_ro('config.json') as cfg:
			for spec in path:
				if spec not in cfg:
					config.logger.error("Path not found")
					return -1
				cfg = cfg.get(spec)
		print(json.dumps(cfg, indent=2))

	if args.set:
		raise NotImplementedError()

