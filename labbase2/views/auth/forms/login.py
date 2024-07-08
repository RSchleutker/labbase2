from labbase2.forms.utils import RENDER_KW
from labbase2.forms.filters import strip_input
from labbase2.forms.filters import make_lower

from flask_wtf import FlaskForm
from wtforms.fields import StringField
from wtforms.fields import PasswordField
from wtforms.fields import BooleanField
from wtforms.fields import SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    """The form used on the login site for users to log in.

    Attributes
    ----------
    user : StringField
        The email of the user. Please note that the email has to be unique
        among all users. Therefore, it can be used as an identifier. The
        username does not have to be unique. Accordingly, it is not suitable
        for logging in.
    password : PasswordField
        The current password of the user.
    remember_me : BooleanField
        ...
    """

    user = StringField(
        "User",
        validators=[DataRequired()],
        filters=[strip_input, make_lower],
        render_kw=RENDER_KW | {"id": "login-form-email",
                               "placeholder": "Username or e-mail address"},
        description="""
        Enter your username or e-mail address.
        """
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired()],
        render_kw=RENDER_KW | {"id": "login-form-password",
                               "placeholder": "Password"},
        description="""
        Enter your password.
        """
    )
    remember_me = BooleanField(
        "Remember me",
        description="""
        Do you want to be kept logged in until you actively log out or delete
        your browser cache?
        """
    )
    submit = SubmitField(
        "Sign In",
        render_kw=RENDER_KW | {"id": "login-form-submit",
                               "class": "btn btn-primary btn-block btn-sm"}
    )
