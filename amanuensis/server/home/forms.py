from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

# from amanuensis.server.forms import User, Lexicon


# class LexiconCreateForm(FlaskForm):
# 	"""/admin/create/"""
# 	lexiconName = StringField(
# 		'Lexicon name',
# 		validators=[DataRequired(), Lexicon(should_exist=False)])
# 	editorName = StringField(
# 		'Username of editor',
# 		validators=[DataRequired(), User(should_exist=True)])
# 	promptText = TextAreaField('Prompt')
# 	submit = SubmitField('Create')
