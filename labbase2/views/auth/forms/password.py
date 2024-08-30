from flask_wtf import FlaskForm
from labbase2.forms import render
from labbase2.forms.validators import (
    AllASCII,
    ContainsLower,
    ContainsNotSpace,
    ContainsNumber,
    ContainsSpecial,
    ContainsUpper,
)
from wtforms.fields import PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Optional

__all__ = ["ChangePassword"]


class ChangePassword(FlaskForm):

    new_password = PasswordField(
        "New password",
        validators=[
            DataRequired(),
            Length(min=12),
            ContainsLower(),
            ContainsUpper(),
            ContainsNumber(),
            ContainsSpecial(),
            ContainsNotSpace(),
            AllASCII(),
        ],
        render_kw=render.custom_field | {"placeholder": "new password"},
        description="""
        Minimum 12 characters. Contains lower- and uppercase characters. Contains at 
        least 1 number. Contains a special character. Does not contain spaces. Only 
        ASCII characters.
        """,
    )
    new_password2 = PasswordField(
        "Repeat new password",
        validators=[DataRequired(), EqualTo("new_password")],
        render_kw=render.custom_field | {"placeholder": "repeat new password"},
    )
    old_password = PasswordField(
        "Old password",
        validators=[Optional()],
        render_kw=render.custom_field | {"placeholder": "old password"},
    )
    submit = SubmitField("Submit", render_kw=render.submit_field)
