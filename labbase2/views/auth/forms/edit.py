import zoneinfo

from flask import current_app
from flask_wtf import FlaskForm
from wtforms.fields import FileField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length

from labbase2.forms import rendering

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
        render_kw=rendering.custom_field | {"placeholder": "First name"},
        description="You given name. You may use initials for middle names.",
    )
    last_name = StringField(
        label="Last name",
        validators=[DataRequired(), Length(max=64)],
        render_kw=rendering.custom_field | {"placeholder": "First name"},
    )
    email = StringField(
        label="E-Mail Address",
        validators=[DataRequired(), Email(), Length(max=128)],
        render_kw=rendering.custom_field
        | {"id": "register-form-email", "placeholder": "Email Address"},
        description="The university email address.",
    )
    timezone = SelectField(
        "Timezone",
        choices=[(tz, tz) for tz in sorted(zoneinfo.available_timezones())],
        default=lambda: current_app.config["DEFAULT_TIMEZONE"],
        validators=[DataRequired()],
        render_kw=rendering.select_field,
        description="Select the timezone in which times shall be displayed for you.",
    )
    file = FileField(
        "Picture",
        render_kw=rendering.file_field,
        description="Ideally use a portrait with 1:1 aspect ratio.",
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired()],
        render_kw=rendering.custom_field | {"placeholder": "Password"},
        description="Verify your password.",
    )
    submit = SubmitField(label="Submit", render_kw=rendering.submit_field)
