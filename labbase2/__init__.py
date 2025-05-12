import json
import secrets
from pathlib import Path
from typing import Optional, Union

from flask import Flask
from sqlalchemy import func, select

from labbase2 import logging, views
from labbase2.database import db
from labbase2.models import Group, Permission, User, events
from labbase2.models.user import login_manager
from labbase2.utils import template_filters

__all__ = ["create_app"]


def create_app(
    config: Optional[Union[str, Path]] = None,
    config_dict: Optional[dict] = None,
    **kwargs,
) -> Flask:
    """Create an app instance of the labbase2 application.

    Parameters
    ----------
    config : Optional[Union[str, Path]]
        A filename pointing to the configuration file. File has to be in JSON format.
        Filename is supposed to be relative to the instance path.
    config_dict : Optional[dict]
        Additional config parameters for the app. If `config` und `config_dict` contain
        the same keys, settings from `config_dict` will be applied.
    kwargs
        Additional parameters passed to the Flask class during instantiation. Supports
        all parameters of the Flask class except `import_name` and
        `instance_relative_config`, which are hardcoded to `labbase2` and `True`
        respectively.

    Returns
    -------
    Flask
        A configured Flask application instance. If run for the first time, an instance
        folder as well as a sub-folder for uploading files and a SQLite database will be
        created.
    """

    app: Flask = Flask("labbase2", instance_relative_config=True, **kwargs)
    app.config.from_object("labbase2.config.DefaultConfig")

    if config is not None:
        app.config.from_file(config, load=json.load, text=False)
    if config_dict is not None:
        app.config |= config_dict

    app.logger.debug("Config dict: %s", config_dict)
    app.logger.debug("Instance path: %s", app.instance_path)

    # Initialize logging.
    logging.init_app(app)

    # Create upload folder if necessary.
    try:
        Path(app.instance_path, app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    except PermissionError as error:
        app.logger.error("Could not create upload folder due to insufficient permissions!")
        raise error

    # Initiate the database.
    db.init_app(app)

    with app.app_context():
        # Create database and add tables (if not yet present).
        db.create_all()

    # Create/update permissions from the config.
    _set_up_permissions(app=app)
    _set_up_groups(app=app)

    # If no user with admin rights is in the database, create one.
    _set_up_admin(app=app)

    # Register login_manager with application.
    login_manager.init_app(app)

    # Register blueprints with application.
    app.register_blueprint(views.base.bp)
    app.register_blueprint(views.auth.bp)
    app.register_blueprint(views.imports.bp)
    app.register_blueprint(views.chemicals.bp)
    app.register_blueprint(views.comments.bp)
    app.register_blueprint(views.files.bp)
    app.register_blueprint(views.fly_stocks.bp)
    app.register_blueprint(views.requests.bp)
    app.register_blueprint(views.batches.bp)
    app.register_blueprint(views.antibodies.bp)
    app.register_blueprint(views.plasmids.bp)
    app.register_blueprint(views.oligonucleotides.bp)

    # Add custom template filters to Jinja2.
    app.jinja_env.filters["format_date"] = template_filters.format_date
    app.jinja_env.filters["format_datetime"] = template_filters.format_datetime
    app.jinja_env.globals["random_string"] = secrets.token_hex

    return app


def _set_up_permissions(app: Flask):
    with app.app_context():
        # Add permissions to database.
        for name, description in app.config.get("PERMISSIONS"):
            if (permission := db.session.get(Permission, name)) is None:
                db.session.add(Permission(name=name, description=description))
            else:
                permission.description = description

        db.session.commit()


def _set_up_groups(app: Flask):
    with app.app_context():
        if not db.session.get(Group, "admin"):
            group = Group(name="admin")
            group.permissions = db.session.scalars(select(Permission)).all()
            db.session.add(group)
            db.session.commit()
        if not db.session.get(Group, "user"):
            group = Group(name="user")
            group.permissions = [db.session.get(Permission, "add-comment")]
            db.session.add(group)
            db.session.commit()


def _set_up_admin(app: Flask):
    with app.app_context():
        first, last, email = app.config.get("USER")

        user_count = select(func.count()).select_from(User)  # pylint: disable=not-callable
        admin_count = (
            select(func.count())  # pylint: disable=not-callable
            .select_from(User)
            .join(User.groups)
            .where(User.is_active, Group.name == "admin")
        )

        if db.session.scalar(user_count) == 0:
            app.logger.info("No user in database; create admin as specified in config.")
            admin = User(first_name=first, last_name=last, email=email)
            admin.set_password("admin")
            db.session.add(admin)
            db.session.commit()
            admin.groups.append(db.session.get(Group, "admin"))
            admin.groups.append(db.session.get(Group, "user"))
            db.session.commit()
        elif db.session.scalar(admin_count) == 0:
            app.logger.info("No active user with admin rights; Re-activate admin.")
            admin = db.session.scalars(select(User).where(User.email == email)).first()
            if admin is not None:
                app.logger.info("Re-activated admin: %s", admin.username)
                admin.groups.append(db.session.get(Group, "admin"))
            else:
                app.logger.info("Did not find admin, create an admin from config.")
                admin = User(first_name=first, last_name=last, email=email, is_admin=True)
                admin.set_password("admin")
                admin.groups.append(db.session.get(Group, "admin"))
                admin.groups.append(db.session.get(Group, "user"))
                db.session.add(admin)

        try:
            db.session.commit()
        except Exception as error:
            app.logger.error("Could not add initial user/admin to database: %s", error)
            raise error
