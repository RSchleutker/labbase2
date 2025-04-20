import json
import secrets
from pathlib import Path
from typing import Optional, Union

from flask import Flask
from labbase2 import logging
from sqlalchemy import select, func


__all__ = ["create_app"]


def create_app(config: Optional[Union[str, Path]] = None, config_dict: Optional[dict] = None, **kwargs) -> Flask:
    """Create an app instance of the labbase2 application.

    Parameters
    ----------
    config : Optional[Union[str, Path]]
        A filename pointing to the configuration file. File has to be in JSON format.
        Filename is supposed to be relative to the instance path.
    config_dict : Optional[dict]
        Additional config parameters for the app. If `config` und `config_dict` contain the same keys, settings from
        `config_dict` will be applied.
    kwargs
        Additional parameters passed to the Flask class during instantiation.
        Supports all parameters of the Flask class except `import_name` and
        `instance_relative_config`, which are hardcoded to `labbase2` and `True`
        respectively.

    Returns
    -------
    Flask
        A configured Flask application instance. If run for the first time,
        an instance folder as well as a sub-folder for uploading files and a SQLite
        database will be created.
    """

    app: Flask = Flask("labbase2", instance_relative_config=True, **kwargs)
    app.config.from_object("labbase2.config.DefaultConfig")

    if config is not None:
        app.config.from_file(config, load=json.load, text=False)
    if config_dict is not None:
        app.config |= config_dict

    # Initialize logging.
    logging.init_app(app)

    # Create upload folder if necessary.
    try:
        Path(app.instance_path, app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    except PermissionError as error:
        app.logger.error("Could not create upload folder due to insufficient permissions!")
        raise error

    # Initiate the database.
    from labbase2.models import db

    db.init_app(app)

    with app.app_context():
        # Create database and add tables (if not yet present).
        db.create_all()

    # Create/update permissions from the config.
    from labbase2.models import Permission, User

    with app.app_context():
        # Add permissions to database.
        for name, description in app.config.get("PERMISSIONS"):
            if (permission := db.session.get(Permission, name)) is None:
                db.session.add(Permission(name=name, description=description))
            else:
                permission.description = description
            db.session.commit()

    from labbase2.models import events

    # If no user with admin rights is in the database, create one.
    with app.app_context():
        first, last, email = app.config.get("USER")

        user_count = db.session.scalar(
            select(func.count())
            .select_from(User)
        )
        admin_count = db.session.scalar(
            select(func.count())
            .select_from(User)
            .where(User.is_active & User.is_admin)
        )

        if user_count == 0:
            app.logger.info("No user in database; create admin as specified in config.")
            admin = User(first_name=first, last_name=last, email=email, is_admin=True)
            admin.set_password("admin")
            admin.permissions = db.session.scalars(select(Permission)).all()
            db.session.add(admin)
        elif admin_count == 0:
            app.logger.info("No active user with admin rights; trying to re-activate admin specified in config.")
            admin = db.session.scalars(select(User).where(User.email == email)).first()
            if admin is not None:
                app.logger.info("Re-activated initial admin '%s' from config.", admin.username)
                admin.is_admin = True
                admin.is_active = True
            else:
                app.logger.info(
                    "Did not find admin user specified in config; create an initial admin from config."
                )
                admin = User(first_name=first, last_name=last, email=email, is_admin=True)
                admin.set_password("admin")
                admin.permissions = db.session.scalars(select(Permission)).all()
                db.session.add(admin)

        app.logger.info("Had %d users and %d admins in database at startup.", user_count, admin_count)

        try:
            db.session.commit()
        except Exception as error:
            app.logger.error("Could not add initial user/admin to database: %s", error)
            raise error

    # Register login_manager with application.
    from labbase2.models.user import login_manager

    login_manager.init_app(app)

    # Register blueprints with application.
    from labbase2 import views

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
    from labbase2.utils import template_filters

    app.jinja_env.filters["format_date"] = template_filters.format_date
    app.jinja_env.filters["format_datetime"] = template_filters.format_datetime
    app.jinja_env.globals["random_string"] = secrets.token_hex

    return app
