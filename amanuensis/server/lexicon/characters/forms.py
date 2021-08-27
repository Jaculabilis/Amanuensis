from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class CharacterCreateForm(FlaskForm):
    """/lexicon/<name>/characters/edit/<character_id>"""

    name = StringField("Character name", validators=[DataRequired()])
    signature = TextAreaField("Signature")
    submit = SubmitField("Submit")
