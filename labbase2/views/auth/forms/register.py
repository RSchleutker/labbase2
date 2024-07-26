from labbase2.forms.utils import RENDER_KW
from labbase2.forms.validators import AllASCII
from labbase2.forms.validators import ContainsNumber
from labbase2.forms.validators import ContainsLower
from labbase2.forms.validators import ContainsUpper
from labbase2.forms.validators import ContainsSpecial
from labbase2.forms.validators import ContainsNotSpace

from flask import current_app
from flask_wtf import FlaskForm
from wtforms.fields import StringField
from wtforms.fields import PasswordField
from wtforms.fields import SubmitField
from wtforms.fields import SelectField
from wtforms.fields import SelectMultipleField
from wtforms.widgets import Select
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import EqualTo
from wtforms.validators import Length
from wtforms.validators import Optional

import zoneinfo


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

    username = StringField(
        label="Name",
        validators=[DataRequired(), Length(max=64)],
        render_kw=RENDER_KW | {"id": "register-form-username",
                               "placeholder": "Username"},
        description="""
        A unique username, typically the first and last name of the person.
        """
    )
    email = StringField(
        label="E-Mail Address",
        validators=[DataRequired(), Email(), Length(max=128)],
        render_kw=RENDER_KW | {"id": "register-form-email",
                               "placeholder": "Email Address"},
        description="""
        The university email address.
        """
    )
    roles = SelectMultipleField(
        "Roles",
        choices=[(-1, "-")],
        coerce=int,
        validators=[Optional()],
        render_kw=RENDER_KW | {"id": "register-form-roles",
                               'size': 5},
        widget=Select(multiple=True),
        description="""
        Select the roles the user should have.
        """
    )
    timezone = SelectField(
        "Timezone",
        choices=[(tz, tz) for tz in zoneinfo.available_timezones()],
        default=current_app.config["DEFAULT_TIMEZONE"],
        validators=[DataRequired()],
        render_kw=RENDER_KW,
        description="Select the timezone in which dates and times shall be displayed for you."
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=12), ContainsLower(),
                    ContainsUpper(), ContainsNumber(), ContainsSpecial(),
                    ContainsNotSpace(), AllASCII()],
        render_kw=RENDER_KW | {"id": "register-form-password",
                               "placeholder": "Password"},
        description="""
        Choose a password. The password should have at least a length of 12 
        characters and contain upper and lower letters, at least one number, 
        and at least one special characters. Only ASCII characters are valid.
        """
    )
    password2 = PasswordField(
        "Repeat Password",
        validators=[DataRequired(), EqualTo("password")],
        render_kw=RENDER_KW | {"id": "register-form-password2",
                               "placeholder": "Repeat Password"},
        description="""
        Repeat the password.
        """
    )
    submit = SubmitField(
        "Submit",
        render_kw=RENDER_KW | {"id": "register-form-submit",
                               "class": "btn btn-primary btn-block btn-sm"}
    )

    def __init__(self, role_choices: list[tuple[int, str]], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.roles.choices += role_choices