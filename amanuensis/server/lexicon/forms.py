from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class LexiconJoinForm(FlaskForm):
    """/lexicon/<name>/join/"""

    password = StringField("Password")
    submit = SubmitField("Submit")
