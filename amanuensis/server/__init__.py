from flask import Flask

from amanuensis.config import RootConfigDirectoryContext
from amanuensis.models import ModelFactory
from amanuensis.server.auth import get_login_manager, bp_auth
from amanuensis.server.helpers import register_custom_filters
from amanuensis.server.home import bp_home
# from amanuensis.server.lexicon import bp_lexicon


def get_app(root: RootConfigDirectoryContext) -> Flask:
	# Flask app init
	with root.read_config() as cfg:
		app = Flask(
			__name__,
			template_folder='../templates',
			static_folder=cfg.static_root
		)
		app.secret_key = bytes.fromhex(cfg.secret_key)
	app.config['root'] = root
	app.config['model_factory'] = ModelFactory(root)
	app.jinja_options['trim_blocks'] = True
	app.jinja_options['lstrip_blocks'] = True
	register_custom_filters(app)

	# Flask-Login init
	login_manager = get_login_manager(root)
	login_manager.init_app(app)

	# Blueprint inits
	app.register_blueprint(bp_auth)
	app.register_blueprint(bp_home)
	# app.register_blueprint(bp_lexicon)

	# import code
	# code.interact(local=locals())

	return app
