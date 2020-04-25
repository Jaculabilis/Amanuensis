# Standard library imports
from collections import OrderedDict
import fcntl
import json
import os
import shutil

# Module imports
from amanuensis.resources import get_stream

from .context import json_ro, json_rw


def create_config_dir(config_dir, refresh=False):
	"""
	Create or refresh a config directory
	"""

	def prepend(*path):
		joined = os.path.join(*path)
		if not joined.startswith(config_dir):
			joined = os.path.join(config_dir, joined)
		return joined

	# Create the directory if it doesn't exist.
	if not os.path.isdir(config_dir):
		os.mkdir(config_dir)

	# The directory should be empty if we're not updating an existing one.
	if len(os.listdir(config_dir)) > 0 and not refresh:
		print("Directory {} is not empty".format(config_dir))
		return -1

	# Update or create global config.
	def_cfg = get_stream("global.json")
	global_config_path = prepend("config.json")
	if refresh and os.path.isfile(global_config_path):
		# We need to write an entirely different ordereddict to the config
		# file, so we mimic the config.context functionality manually.
		with open(global_config_path, 'r+', encoding='utf8') as cfg_file:
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
		with open(prepend("config.json"), 'wb') as f:
			f.write(def_cfg.read())

	# Ensure lexicon subdir exists.
	if not os.path.isdir(prepend("lexicon")):
		os.mkdir(prepend("lexicon"))
	if not os.path.isfile(prepend("lexicon", "index.json")):
		with open(prepend("lexicon", "index.json"), 'w') as f:
			json.dump({}, f)

	# Ensure user subdir exists.
	if not os.path.isdir(prepend("user")):
		os.mkdir(prepend("user"))
	if not os.path.isfile(prepend('user', 'index.json')):
		with open(prepend('user', 'index.json'), 'w') as f:
			json.dump({}, f)

	if refresh:
		for dir_name in ('lexicon', 'user'):
			# Clean up unindexed folders
			with json_ro(prepend(dir_name, 'index.json')) as index:
				known = list(index.values())
			entries = os.listdir(prepend(dir_name))
			for dir_entry in entries:
				if dir_entry == "index.json":
					continue
				if dir_entry in known:
					continue
				print("Removing unindexed folder: '{}/{}'"
					.format(dir_name, dir_entry))
				shutil.rmtree(prepend(dir_name, dir_entry))

			# Remove orphaned index listings
			with json_rw(prepend(dir_name, 'index.json')) as index:
				for name, entry in index.items():
					if not os.path.isdir(prepend(dir_name, entry)):
						print("Removing stale {} index entry '{}: {}'"
							.format(dir_name, name, entry))
						del index[name]
