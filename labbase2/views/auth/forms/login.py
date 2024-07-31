from flask_wtf import FlaskForm
from labbase2.forms import render
from labbase2.forms.filters import make_lower, strip_input
from wtforms.fields import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    """The form used on the login site for users to log in.

    Attributes
    ----------
    email : StringField
        The email of the user. Please note that the email has to be unique among all
        users. Therefore, it can be used as an identifier. The username does not have
        to be unique. Accordingly, it is not suitable for logging in.
    password : PasswordField
        The current password of the user.
    remember_me : BooleanField
        ...
    """

    email = StringField(
        "User",
        validators=[DataRequired()],
        filters=[strip_input, make_lower],
        render_kw=render.custom_field | {"placeholder": "E-mail address"},
        description="""
        Enter your E-mail address.
        """,
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired()],
        render_kw=render.custom_field | {"placeholder": "Password"},
        description="""
        Enter your password.
        """,
    )
    remember_me = BooleanField(
        "Remember me",
        render_kw=render.boolean_field,
        description="""
        Do you want to be kept logged in until you actively log out or delete
        your browser cache?
        """,
    )
    submit = SubmitField("Sign In", render_kw=render.submit_field)
