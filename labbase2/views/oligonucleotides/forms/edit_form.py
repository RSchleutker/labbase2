from datetime import date

from flask import render_template
from flask_login import current_user
from labbase2.forms import EditEntityForm, render
from labbase2.forms.filters import remove_whitespaces, strip_input
from labbase2.forms.validators import AllowCharacters
from labbase2.models import User
from wtforms.fields import DateField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

__all__ = ["EditOligonucleotide"]


class EditOligonucleotide(EditEntityForm):
    date_ordered = DateField(
        "Order date",
        default=date.today,
        validators=[Optional()],
        render_kw=render.custom_field
        | {"type": "date", "placeholder": "Primer name, e.g. oRS-1"},
    )
    owner_id = SelectField(
        "Owner",
        validators=[DataRequired()],
        validate_choice=False,
        default=lambda: current_user.id,
        coerce=int,
        render_kw=render.select_field,
        description="""
        Be aware that you cannot edit this entry anymore if you select someone else.
        """,
    )
    sequence = StringField(
        "Sequence",
        validators=[DataRequired(), Length(max=256), AllowCharacters("ACGTacgt")],
        filters=[strip_input, remove_whitespaces],
        render_kw=render.custom_field | {"placeholder": "Sequence"},
    )
    storage_place = StringField(
        "Storage place",
        validators=[Optional(), Length(max=64)],
        filters=[strip_input],
        render_kw=render.custom_field | {"placeholder": "Storage place"},
    )
    description = TextAreaField(
        "Description",
        validators=[Optional(), Length(max=512)],
        filters=[strip_input],
        render_kw=render.custom_field | {"placeholder": "Description", "rows": 6},
        description="""
        Give a short description about the purpose of this oligonucleotide.
        """,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = User.query.with_entities(User.id, User.username)
        choices = [tuple(choice) for choice in choices]
        self.owner_id.choices = choices

    def render(self, action: str = "", method: str = "GET") -> str:
        return render_template(
            "oligonucleotides/form.html", form=self, action=action, method=method
        )
