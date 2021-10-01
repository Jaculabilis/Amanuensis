import uuid

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    FieldList,
    FormField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import Optional, DataRequired, ValidationError
from wtforms.widgets.html5 import NumberInput

from amanuensis.db import IndexType, Lexicon


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
    allow_post = BooleanField("Allow players to make posts")
    submit = SubmitField("Submit")


def parse_index_type(type_str):
    if not type_str:
        return None
    return getattr(IndexType, type_str)


class IndexDefinitionForm(FlaskForm):
    """/lexicon/<name>/settings/index/"""

    class Meta:
        # Disable CSRF on the individual index definitions, since the schema
        # form will have one
        csrf = False

    TYPE_CHOICES = [("", "")] + [(str(t), str(t).lower()) for t in IndexType]

    index_type = SelectField(choices=TYPE_CHOICES, coerce=parse_index_type)
    pattern = StringField()
    logical_order = IntegerField(
        widget=NumberInput(min=-99, max=99), validators=[Optional()]
    )
    display_order = IntegerField(
        widget=NumberInput(min=-99, max=99), validators=[Optional()]
    )
    capacity = IntegerField(widget=NumberInput(min=0, max=99), validators=[Optional()])

    def validate_pattern(form, field):
        if form.index_type.data and not field.data:
            raise ValidationError("Pattern must be defined")


class IndexSchemaForm(FlaskForm):
    """/lexicon/<name>/settings/index/"""

    indices = FieldList(FormField(IndexDefinitionForm))
    submit = SubmitField("Submit")


def parse_uuid(uuid_str):
    if not uuid_str:
        return None
    return uuid.UUID(uuid_str)


class AssignmentDefinitionForm(FlaskForm):
    """/lexicon/<name>/settings/assign/"""

    class Meta:
        # Disable CSRF on the individual assignment definitions, since the
        # schema form will have one
        csrf = False

    turn = IntegerField(widget=NumberInput(min=0, max=99))
    index = SelectField()
    character = SelectField(coerce=parse_uuid)


class IndexAssignmentsForm(FlaskForm):
    """/lexicon/<name>/settings/assign/"""

    rules = FieldList(FormField(AssignmentDefinitionForm))
    submit = SubmitField("Submit")

    def populate(self, lexicon: Lexicon):
        """Populate the select fields with indices and characters"""
        index_choices = []
        for i in lexicon.indices:
            index_choices.append((i.name, i.pattern))
        char_choices = [("", "")]
        for c in lexicon.characters:
            char_choices.append((str(c.public_id), c.name))
        for rule in self.rules:
            rule.index.choices = index_choices
            rule.character.choices = char_choices
