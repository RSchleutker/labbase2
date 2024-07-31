import zoneinfo

from flask import current_app
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
from wtforms.fields import PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

__all__ = ["RegisterForm"]


class RegisterForm(FlaskForm):
    """A registration form for new users.

    Attributes
    ----------
    username : StringField
    email : StringField
    roles : SelectField
    password : PasswordField
    password2 : PasswordField
    submit : SubmitField

    Notes
    -----
    The registration form is thought to be exposed only to an administrator
    of the site since the users should not be allowed to choose their own roles.
    """

    first_name = StringField(
        label="First name",
        validators=[DataRequired(), Length(max=64)],
        render_kw=render.custom_field | {"placeholder": "First name"},
        description="You given name. You may use initials for middle names.",
    )
    last_name = StringField(
        label="Last name",
        validators=[DataRequired(), Length(max=64)],
        render_kw=render.custom_field | {"placeholder": "Last name"},
    )
    email = StringField(
        label="E-Mail Address",
        validators=[DataRequired(), Email(), Length(max=128)],
        render_kw=render.custom_field | {"placeholder": "Email Address"},
        description="The university email address.",
    )
    timezone = SelectField(
        "Timezone",
        choices=[(tz, tz) for tz in sorted(zoneinfo.available_timezones())],
        default=lambda: current_app.config["DEFAULT_TIMEZONE"],
        validators=[DataRequired()],
        render_kw=render.select_field,
        description="""
        Select the timezone in which dates and times shall be displayed for you.
        """,
    )
    password = PasswordField(
        "Password",
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
        render_kw=render.custom_field | {"placeholder": "Password"},
        description="""
        Minimum 12 characters. Contains lower- and uppercase characters. Contains at 
        least 1 number. Contains a special character. Does not contain spaces. Only 
        ASCII characters.
        """,
    )
    password2 = PasswordField(
        "Repeat Password",
        validators=[DataRequired(), EqualTo("password")],
        render_kw=render.custom_field | {"placeholder": "Repeat Password"},
    )
    submit = SubmitField("Submit", render_kw=render.submit_field)
