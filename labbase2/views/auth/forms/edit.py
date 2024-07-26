from labbase2.forms.utils import RENDER_KW
from labbase2.forms.utils import RENDER_KW_FILE
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
from wtforms.fields import FileField
from wtforms.widgets import Select
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import EqualTo
from wtforms.validators import Length
from wtforms.validators import Optional

import zoneinfo


__all__ = ["EditUserForm"]


class EditUserForm(FlaskForm):
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
        render_kw=RENDER_KW | {"placeholder": "First name"},
        description="""
        A unique username, typically the first and last name of the person.
        """
    )
    last_name = StringField(
        label="Last name",
        validators=[DataRequired(), Length(max=64)],
        render_kw=RENDER_KW | {"placeholder": "First name"},
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
    timezone = SelectField(
        "Timezone",
        choices=[(tz, tz) for tz in sorted(zoneinfo.available_timezones())],
        default=lambda: current_app.config["DEFAULT_TIMEZONE"],
        validators=[DataRequired()],
        render_kw={"class": "form-select form-select-sm"},
        description="Select the timezone in which dates and times shall be displayed for you."
    )
    file = FileField(
        "Picture",
        render_kw=RENDER_KW_FILE
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired()],
        render_kw=RENDER_KW | {"placeholder": "Password"},
        description="Verify your password."
    )
    submit = SubmitField(
        "Submit",
        render_kw=RENDER_KW | {"id": "register-form-submit",
                               "class": "btn btn-primary btn-block btn-sm"}
    )
