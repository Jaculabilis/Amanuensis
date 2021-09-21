from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired


class CreatePostForm(FlaskForm):
    """/lexicon/<name>/posts/"""

    body = TextAreaField(validators=[DataRequired()])
    submit = SubmitField("Post")
