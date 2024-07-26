from flask import Blueprint
from flask import Response
from flask import flash
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user
from sqlalchemy import func
from sqlalchemy.exc import DataError
from email_validator import validate_email

from .forms.login import LoginForm
from .forms.register import RegisterForm
from .forms.edit import EditUserForm
from .forms.password import ChangePassword
from labbase2.models import db
from labbase2.models import User
from labbase2.models import UserRole
from labbase2.models import BaseFile
from labbase2.utils.role_required import role_required
from labbase2.utils.message import Message
from labbase2.views.files.routes import upload_file


__all__ = ["bp", "login"]


# The blueprint to register all coming blueprints with.
bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
    template_folder="templates"
)


# @bp.route("/", methods=["GET"])
# @login_required
# def index():
#     return render_template("user/index.html", user=current_user)


@bp.route("/login", methods=["GET", "POST"])
def login() -> str | Response:
    # Current user is already authenticated.
    if current_user.is_authenticated:
        flash("You are already logged in!", "warning")
        return redirect(url_for("base.index"))

    form = LoginForm()

    # POST fork with correct credentials.
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if not user:
            flash("Invalid email address or username!", "danger")
        elif not user.is_active:
            flash("Your account is inactive! Get in touch with an admin!", "warning")
        elif not user.verify_password(form.password.data):
            flash("Wrong password!", "danger")
        else:
            login_user(user, remember=form.remember_me.data)

            user.timestamp_last_login = func.now()
            db.session.commit()

            flash("Successfully logged in!", "success")
            next_page = request.args.get("next")

            if not next_page: # or url_parse(next_page).netloc:
                next_page = url_for("base.index")

            return redirect(next_page)

    # GET fork or POST with wrong credentials.
    return render_template("auth/login.html", title="Login", login_form=form)


@bp.route("/logout", methods=["GET"])
@login_required
def logout() -> str | Response:
    logout_user()
    return redirect(url_for(".login"))


@bp.route("/register", methods=["GET", "POST"])
@login_required
@role_required(["User Editor"])
def register() -> str:
    role_choices = UserRole.query.with_entities(UserRole.id, UserRole.name)
    form = RegisterForm(role_choices=role_choices)

    # POST fork of view.
    if form.validate_on_submit():
        username = form.username.data
        email = validate_email(form.email.data).email

        if User.query.filter(User.username.ilike(username)).count() > 0:
            flash("Username already exists!", "danger")
        elif User.query.filter(User.email.ilike(email)).count() > 0:
            flash("Email address already exists!", "danger")
        else:
            user = User(username=username, email=email)
            user.roles = [
                UserRole.query.get(id_) for id_ in form.roles.data
                if id_ > 0
            ]
            user.set_password(form.password.data)

            try:
                db.session.add(user)
                db.session.commit()
            except DataError as error:
                flash(str(error), "danger")
                db.session.rollback()
            else:
                flash("Successfully registered new user!", "success")

    elif form.submit():
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "danger")

    return render_template("auth/register.html", title="Register", form=form)


@bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit_user():
    if request.method == "GET":
        form = EditUserForm(None, obj=current_user)
        return render_template("auth/edit-user.html", form=form)

    form = EditUserForm()

    if not form.validate():
        for error in form.errors:
            flash(str(error), "danger")
        return render_template("auth/edit-user.html", form=form)

    if not current_user.verify_password(form.password.data):
        flash("Password is incorrect!", "danger")
    else:
        form.populate_obj(current_user)

        if form.file.data:
            file = upload_file(form, BaseFile)
            current_user.picture = file

        db.session.commit()

    flash("Successfully edited user profile!", "success")

    return render_template("auth/edit-user.html", form=form)


@bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePassword()

    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash("Your password has been updated!", "success")
        else:
            flash("Old password incorrect!", "danger")

    return render_template(
        "auth/change-password.html",
        form=form
    )
