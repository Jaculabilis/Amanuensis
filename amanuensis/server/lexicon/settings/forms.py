from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    IntegerField,
    PasswordField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import Optional, DataRequired
from wtforms.widgets.html5 import NumberInput


class PlayerSettingsForm(FlaskForm):
    """/lexicon/<name>/settings/player/"""

    notify_ready = BooleanField("Notify me when an article is submitted for review")
    notify_reject = BooleanField("Notify me when an editor rejects one of my articles")
    notify_approve = BooleanField(
        "Notify me when an editor approves one of my articles"
    )
    submit = SubmitField("Submit")


class SetupSettingsForm(FlaskForm):
    """/lexicon/<name>/settings/setup/"""

    title = StringField("Title override")
    prompt = TextAreaField("Prompt", validators=[DataRequired()])
    public = BooleanField("Make game publicly visible")
    joinable = BooleanField("Allow players to join game")
    has_password = BooleanField("Require password to join the game")
    password = PasswordField("Game password")
    turn_count = IntegerField(
        "Number of turns", widget=NumberInput(), validators=[DataRequired()]
    )
    player_limit = IntegerField(
        "Maximum number of players", widget=NumberInput(), validators=[Optional()]
    )
    character_limit = IntegerField(
        "Maximum number of characters per player",
        widget=NumberInput(),
        validators=[Optional()],
    )
    submit = SubmitField("Submit")
