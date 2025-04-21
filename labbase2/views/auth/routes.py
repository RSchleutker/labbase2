import secrets
from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from email_validator import validate_email
from flask import Blueprint, Response
from flask import current_app as app
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from labbase2.models import BaseFile, Permission, ResetPassword, User, db
from labbase2.utils.permission_required import permission_required
from labbase2.views.files.routes import upload_file
from sqlalchemy import select, func
from sqlalchemy.exc import DataError

from .forms.edit import EditUserForm
from .forms.edit_permissions import EditPermissions
from .forms.login import LoginForm
from .forms.password import ChangePassword
from .forms.register import RegisterForm

__all__ = ["bp", "login"]


# The blueprint to register all coming blueprints with.
bp = Blueprint("auth", __name__, url_prefix="/auth", template_folder="templates")


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
        user = db.session.scalar(select(User).where(User.email == form.email.data))

        if not user:
            app.logger.warning("Login attempt with invalid credentials")
            flash("Invalid email address or username!", "danger")
        elif not user.is_active:
            app.logger.info("Deactivate user tried to log in: %s", user.username)
            flash("Your account is inactive! Get in touch with an admin!", "warning")
        elif not user.verify_password(form.password.data):
            app.logger.warning("Login attempt with invalid password: %s", user.username)
            flash("Wrong password!", "danger")
        else:
            login_user(user, remember=form.remember_me.data)
            app.logger.info("Logged in: %s", user.username)
            flash("Successfully logged in!", "success")

            last_login = current_user.timestamp_last_login
            if last_login is None:
                flash("This is your first log in!", "info")
            else:
                tz = current_user.timezone
                formatted = last_login.astimezone(ZoneInfo(tz)).strftime("%B %d, %Y %I:%M %p")
                flash(f"Last login was on {formatted}!", "info")

            user.timestamp_last_login = func.now()
            try:
                db.session.commit()
            except Exception as error:
                db.error("Unable to save login time due to unknown database error: %s", error)

            next_page = request.args.get("next")

            if not next_page:  # or url_parse(next_page).netloc:
                next_page = url_for("base.index")

            return redirect(next_page)

    # GET fork or POST with wrong credentials.
    return render_template("auth/login.html", title="Login", login_form=form)


@bp.route("/logout", methods=["GET"])
@login_required
def logout() -> str | Response:
    app.logger.info("Logged out.")
    flash("Successfully logged out!", "success")

    logout_user()

    return redirect(url_for(".login"))


@bp.route("/register", methods=["GET", "POST"])
@login_required
@permission_required("Manage users")
def register():
    form = RegisterForm()

    # POST fork of view.
    if form.validate_on_submit():
        email = validate_email(form.email.data).normalized

        user_count_stm = select(func.count()).select_from(User).where(User.email == email)
        if db.session.scalar(user_count_stm) > 0:
            app.logger.warning("Tried to register new user with existing email address: %s", email)
            flash("Email address already exists!", "danger")
        else:
            user = User()
            form.populate_obj(user)
            user.email = email
            user.set_password(form.password.data)

            try:
                db.session.add(user)
                db.session.commit()
            except DataError as error:
                app.logger.warning("Could not write new user to database: %s", error)
                flash(str(error), "danger")
                db.session.rollback()
            else:
                app.logger.info("Registered new user: %s", user.username)
                flash("Successfully registered new user!", "success")

    elif form.submit():
        app.logger.warning("Could not register new user due to invalid input: %s", form.data)
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "danger")

    return render_template("auth/register.html", title="Register", form=form)


@bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit_user():
    if request.method == "GET":
        form = EditUserForm(None, obj=current_user)
        return render_template("auth/edit-user.html", title="Edit profile", form=form)

    form = EditUserForm()

    if not form.validate():
        app.logger.warning("Could not edit user due to invalid input.")
        for error in form.errors:
            flash(str(error), "danger")
        return render_template("auth/edit-user.html", title="Edit profile", form=form)

    if not current_user.verify_password(form.password.data):
        app.logger.warning("Entered incorrect password.")
        flash("Password is incorrect!", "danger")
    else:
        form.populate_obj(current_user)

        if form.file.data:
            file = upload_file(form, BaseFile)
            current_user.picture = file
            file.resize(512)

        try:
            db.session.commit()
        except Exception as error:
            app.logger.warning("Could not update user: %s", error)
            flash(str(error), "error")
            db.session.rollback()
        else:
            app.logger.info("Updated user profile.")
            flash("Successfully edited user profile!", "success")

    return render_template("auth/edit-user.html", title="Edit profile", form=form)


@bp.route("/change-password", methods=["GET", "POST"], defaults={"key": None})
@bp.route("/change-password/<string:key>", methods=["GET", "POST"])
@login_required
def change_password(key: Optional[str] = None):
    if key and (reset := db.session.get(ResetPassword, key)) is not None:
        if datetime.now() > reset.timeout:
            flash("Token to reset password has expired!")
            db.session.delete(reset)
        else:
            user = reset.user
            logout_user()
            login_user(user)

    form = ChangePassword()

    if form.validate_on_submit():

        if reset is not None:
            reset.user.set_password(form.new_password.data)
            reset.user.resets.clear()
            updated = True

        elif current_user.verify_password(form.old_password.data):
            current_user.set_password(form.new_password.data)
            updated = True

        else:
            flash("Old password incorrect!", "danger")
            updated = False

        if updated:
            try:
                db.session.commit()
            except Exception as error:
                db.session.rollback()
                flash(str(error), "danger")
            else:
                flash("Your password has been updated!", "success")

    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(": ".join([field, error]), "danger")

    return render_template("auth/change-password.html", form=form)


@bp.route("/change-permissions", methods=["GET"], defaults={"id_": None})
@bp.route("/change-permissions/<int:id_>", methods=["GET", "POST"])
@login_required
@permission_required("Manage users")
def change_permissions(id_: int = None):
    users = db.session.scalars(
        select(User).where(User.is_active).order_by(User.last_name, User.first_name)
    )

    if id_ is None:
        user = current_user
    else:
        user = db.session.get(User, id_)

    form = EditPermissions(**user.form_permissions)

    if form.validate_on_submit():
        user.permissions.clear()
        for field in form:
            if not field.type == "BooleanField":
                continue
            if not field.data:
                continue

            permission = db.session.get(Permission, field.name.replace("_", " ").capitalize())
            user.permissions.append(permission)

        db.session.commit()
        app.logger.info("Updated permissions for user: %s", user.username)
        flash(f"Successfully updated permissions for {user.username}!", "success")

    return render_template(
        "auth/edit-permissions.html",
        form=form,
        selected_user=user,
        users=users,
    )


@bp.route("/change-admin-status/<int:id_>", methods=["GET"])
@login_required
@permission_required("Manage users")
def change_admin_status(id_: int):
    user = db.session.get(User, id_)

    if user is None:
        flash(f"No user with ID {id_})!", "danger")
    else:
        user.is_admin = not user.is_admin

        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            flash(str(error), "danger")
        else:
            flash(f"Successfully changed admin setting for {user.username}!", "success")

    user_count_stm = select(func.count()).select_from(User).where(User.is_admin)
    if db.session.scalar(user_count_stm) == 0:
        flash("No user with admin rights! Reverting previous change!", "warning")
        user.is_admin = True
        db.session.commit()

    if request.referrer is None:
        return redirect(url_for(".users"))
    else:
        return redirect(request.referrer)


@bp.route("/change-active-status/<int:id_>", methods=["GET"])
@login_required
@permission_required("Manage users")
def change_active_status(id_: int):
    user = db.session.get(User, id_)

    if user is None:
        flash(f"No user with ID {id_})!", "danger")
    else:
        user.is_active = not user.is_active

        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            flash(str(error), "danger")
        else:
            flash(f"Successfully changed active setting for {user.username}!", "success")

    user_count_stm = select(func.count()).select_from(User).where(User.is_active)
    if db.session.scalar(user_count_stm) == 0:
        flash("No active user! Reverting previous change!", "warning")
        user.is_active = True
        db.session.commit()

    if request.referrer is None:
        return redirect(url_for(".users"))
    else:
        return redirect(request.referrer)


@bp.route("/reset-password/<int:id_>", methods=["GET"])
@login_required
@permission_required("Manage users")
def create_password_reset(id_: int):
    user = db.session.get(User, id_)

    if user is None:
        flash(f"No user with ID {id_})!", "danger")
        return redirect(request.referrer)

    user.resets.clear()

    db.session.commit()

    expires_after = app.config.get("RESET_EXPIRES", 10)
    reset = ResetPassword(
        token=secrets.token_urlsafe(32),
        user_id=id_,
        timeout=datetime.now() + timedelta(minutes=expires_after),
    )

    db.session.add(reset)
    db.session.commit()

    flash(f"Generated a password reset . Expires: {reset.timeout.isoformat()}!", "success")
    flash(f"Visit: {url_for('auth.change_password', key=reset.token)}")

    if request.referrer is None:
        return redirect(url_for(".users"))
    else:
        return redirect(request.referrer)


@bp.route("/users", methods=["GET"])
@login_required
def users():
    users = db.session.scalars(
        select(User).order_by(
            User.is_active.desc(), User.is_admin.desc(), User.last_name, User.first_name
        )
    )
    return render_template("auth/users.html", users=users, title="Users")
