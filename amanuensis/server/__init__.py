from flask import Flask

from amanuensis.config import RootConfigDirectoryContext
from amanuensis.models import ModelFactory
from .auth import get_login_manager, bp_auth
from .helpers import register_custom_filters
from .home import bp_home
from .lexicon import bp_lexicon
from .session import bp_session


def get_app(root: RootConfigDirectoryContext) -> Flask:
	# Flask app init
	with root.read_config() as cfg:
		app = Flask(
			__name__,
			template_folder='.',
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
	app.register_blueprint(bp_lexicon)
	app.register_blueprint(bp_session)

	return app
