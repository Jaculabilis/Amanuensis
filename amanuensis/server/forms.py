from flask import current_app
from wtforms.validators import ValidationError

from amanuensis.config import RootConfigDirectoryContext


# Custom validators
def User(should_exist: bool = True):
	template: str = 'User "{{}}" {}'.format(
		"not found" if should_exist else "already exists")
	should_exist_copy: bool = bool(should_exist)

	def validate_user(form, field):
		root: RootConfigDirectoryContext = current_app.config['root']
		with root.user.read_index() as index:
			if (field.data in index.keys()) != should_exist_copy:
				raise ValidationError(template.format(field.data))

	return validate_user


def Lexicon(should_exist: bool = True):
	template: str = 'Lexicon "{{}}" {}'.format(
		"not found" if should_exist else "already exists")
	should_exist_copy: bool = bool(should_exist)

	def validate_lexicon(form, field):
		root: RootConfigDirectoryContext = current_app.config['root']
		with root.lexicon.read_index() as index:
			if (field.data in index.keys()) != should_exist_copy:
				raise ValidationError(template.format(field.data))

	return validate_lexicon
