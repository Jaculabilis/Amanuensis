from flask import Blueprint, render_template, url_for
from flask_login import login_required, current_user

import config
import user

def get_bp():
	"""Create a blueprint for pages outside of a specific lexicon"""
	bp = Blueprint('home', __name__, url_prefix='/home')

	@bp.route('/', methods=['GET'])
	@login_required
	def home():
		return render_template(
			'home/home.html',
			sidebar_rows=[current_user.get('username'), current_user.get('displayname'), current_user.uid])

	return bp
