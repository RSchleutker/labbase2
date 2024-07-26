from labbase2.forms.utils import RENDER_KW
from flask_wtf import FlaskForm
from wtforms.fields import PasswordField
from wtforms.fields import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import EqualTo
from wtforms.validators import Length

from labbase2.forms.validators import AllASCII
from labbase2.forms.validators import ContainsNumber
from labbase2.forms.validators import ContainsLower
from labbase2.forms.validators import ContainsUpper
from labbase2.forms.validators import ContainsSpecial
from labbase2.forms.validators import ContainsNotSpace


__all__ = ["ChangePassword"]


class ChangePassword(FlaskForm):

    new_password = PasswordField(
        "New password",
        validators=[DataRequired(), Length(min=12), ContainsLower(),
                    ContainsUpper(), ContainsNumber(), ContainsSpecial(),
                    ContainsNotSpace(), AllASCII()],
        render_kw=RENDER_KW | {"placeholder": "new password"}
    )
    new_password2 = PasswordField(
        "Repeat new password",
        validators=[DataRequired(), EqualTo("new_password")],
        render_kw=RENDER_KW | {"placeholder": "repeat new password"}
    )
    old_password = PasswordField(
        "Old password",
        validators=[DataRequired()],
        render_kw=RENDER_KW | {"placeholder": "old password"}
    )
    submit = SubmitField(
        "Submit",
        render_kw=RENDER_KW | {"class": "btn btn-primary btn-block btn-sm"}
    )
