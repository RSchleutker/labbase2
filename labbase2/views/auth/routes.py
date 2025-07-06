import secrets
from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from email_validator import validate_email
from flask import Blueprint, Response
from flask import current_app as app
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func, select
from sqlalchemy.exc import DataError

from labbase2.database import db
from labbase2.models import BaseFile, Group, Permission, ResetPassword, User
from labbase2.utils.permission_required import permission_required
from labbase2.views.files.routes import upload_file

from .forms.edit import EditUserForm
from .forms.edit_permissions import EditPermissions
from .forms.groups import AddGroupForm, ChangeGroupsForm, EditGroupForm
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

            user.timestamp_last_login = func.now()  # pylint: disable=not-callable
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
@permission_required("register-user")
def register():
    form = RegisterForm()

    # POST fork of view.
    if form.validate_on_submit():
        email = validate_email(form.email.data).normalized

        user_count_stm = (
            select(func.count())  # pylint: disable=not-callable
            .select_from(User)
            .where(User.email == email)
        )
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

    elif request.method.lower() == "post":
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
    if key is not None:
        reset = db.session.get(ResetPassword, key)
        if not reset:
            flash("Invalid token!", "danger")
            return redirect(url_for("auth.change_password"))
        if datetime.now() > reset.timeout:
            flash("Token to reset password has expired!")
            db.session.delete(reset)
            return redirect(url_for("auth.change_password"))
        user = reset.user
        logout_user()
        login_user(user)
    else:
        reset = None
        user = current_user

    form = ChangePassword()

    if request.method == "GET":
        return render_template("auth/change-password.html", form=form)

    if not form.validate():
        flash(f"{form.errors}", "danger")

    if not reset and not current_user.verify_password(form.old_password.data):
        flash("Old password incorrect!", "danger")
        render_template("auth/change-password.html", form=form)

    user.set_password(form.new_password.data)
    user.resets.clear()

    try:
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        flash(str(error), "danger")
    else:
        flash("Your password has been updated!", "success")

    return render_template("auth/change-password.html", form=form)


@bp.route("/change-permissions", methods=["GET"], defaults={"id_": None})
@bp.route("/change-permissions/<int:id_>", methods=["GET", "POST"])
@login_required
@permission_required("change-group")
def change_permissions(id_: int = None):
    users_stmt = select(User).where(User.is_active).order_by(User.last_name, User.first_name)

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
        users=db.session.scalars(users_stmt).all(),
    )


@bp.route("/change-admin-status/<int:id_>", methods=["GET"])
@login_required
@permission_required("change-group")
def change_admin_status(id_: int):
    user = db.session.get(User, id_)
    admin_group = db.session.get(Group, "admin")

    if user is None:
        flash(f"No user with ID {id_})!", "danger")
        return redirect(url_for(".users"))

    if admin_group in user.groups:
        user.groups.remove(admin_group)
    else:
        user.groups.append(admin_group)

    try:
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        flash(str(error), "danger")
    else:
        flash(f"Successfully changed admin setting for {user.username}!", "success")

    user_count_stm = (
        select(func.count())  # pylint: disable=not-callable
        .select_from(User)
        .join(User.groups)
        .where(Group.name == "admin")
    )
    if db.session.scalar(user_count_stm) == 0:
        flash("No user with admin rights! Reverting previous change!", "warning")
        user.groups.append(admin_group)
        db.session.commit()

    return redirect(url_for(".users"))


@bp.route("/change-active-status/<int:id_>", methods=["GET"])
@login_required
@permission_required("inactivate-user")
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

    user_count_stm = (
        select(func.count()).select_from(User).where(User.is_active)  # pylint: disable=not-callable
    )
    if db.session.scalar(user_count_stm) == 0:
        flash("No active user! Reverting previous change!", "warning")
        user.is_active = True
        db.session.commit()

    if request.referrer is None:
        return redirect(url_for(".users"))

    return redirect(request.referrer)


@bp.route("/reset-password/<int:id_>", methods=["GET"])
@login_required
@permission_required("reset-password")
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

    return redirect(request.referrer)


@bp.route("/users", methods=["GET"])
@login_required
@permission_required("view-user")
def users():
    entities = db.session.scalars(
        select(User).order_by(User.is_active.desc(), User.last_name, User.first_name)
    )
    return render_template("auth/users.html", users=entities, title="Users")


@bp.route("/groups", methods=["GET"])
@login_required
@permission_required("edit-groups")
def index_groups():
    entities = db.session.scalars(
        select(Group).where(Group.name.notin_(["admin", "user"])).order_by(Group.name.asc())
    )

    return render_template("auth/groups.html", groups=entities, title="Groups")


@bp.route("/groups/add", methods=["GET", "POST"])
@login_required
@permission_required("edit-groups")
def add_group():
    form = AddGroupForm()

    if request.method == "GET":
        return render_template("auth/add-group.html", form=form)

    # This is required as fields for permissions are dynamically added.
    form.process(formdata=request.form)

    if not form.validate():
        app.logger.info("Couldn't add group due to invalid input.")
        flash(f"{form.errors}", "warning")

    group = Group()
    group.name = form.name.data
    group.description = form.description.data
    group.permissions = form.selected_permissions

    try:
        db.session.add(group)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        app.logger.warning("Couldn't add group due to unknown database error: %s", error)
        flash(str(error), "warning")
    else:
        flash(f"Successfully added group '{group.name}' to database.", "success")

    return render_template("auth/add-group.html", form=form)


@bp.route("/groups/<string:id_>", methods=["GET", "POST"])
@login_required
@permission_required("edit-groups")
def edit_group(id_: str):
    if not (group := db.session.get(Group, id_)):
        flash(f"No group with name {id_}!", "warning")
        return redirect(request.referrer)

    if group.name in ["user", "admin"]:
        flash("'user' and 'admin' groups cannot be edited!", "warning")
        return redirect(request.referrer)

    form = EditGroupForm(obj=group, group_name=id_)

    if request.method == "GET":
        return render_template("auth/edit-group.html", form=form, group=group)

    # This is required as fields for permissions are dynamically added.
    form.process(formdata=request.form)

    if not form.validate():
        flash(f"{form.errors}", "warning")
        return render_template("auth/edit-group.html", form=form, group=group)

    group.description = form.description.data
    group.permissions = form.selected_permissions

    try:
        db.session.commit()
    except Exception as error:
        flash(f"Could not edit group: {error}", "warning")
        db.session.rollback()
    else:
        flash(f"Successfully edited group {group.name}!", "success")

    return render_template("auth/edit-group.html", form=form, group=group)


@bp.route("users/groups/<int:id_>", methods=["GET", "POST"])
@login_required
@permission_required("change-group")
def change_groups(id_: int):
    if not (user := db.session.get(User, id_)):
        flash(f"No user with ID {id_}!", "warning")
        return redirect(request.referrer)

    form = ChangeGroupsForm(user_id=id_)

    if request.method == "GET":
        return render_template("auth/change-groups.html", form=form, user=user)

    # Required because fields are dynamically added to the form.
    form.process(formdata=request.form)

    if not form.validate():
        flash(f"{form.errors}", "warning")
        return render_template("auth/change-groups.html", form=form, user=user)

    protected_groups = db.session.scalars(
        select(Group).where(Group.name.in_(["admin", "user"]), Group.users.any(User.id == id_))
    ).all()

    user.groups = form.selected_groups + protected_groups

    try:
        db.session.commit()
    except Exception as error:
        flash(f"Could not change groups! {error}", "warning")
        db.session.rollback()
    else:
        flash("Successfully changed groups!", "success")

    return render_template("auth/change-groups.html", form=form, user=user)
