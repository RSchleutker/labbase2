import json
import secrets
from pathlib import Path
from typing import Optional, Union

from flask import Flask, request


__all__ = ["create_app"]


def create_app(config: Optional[Union[str, Path]] = None, config_dict: Optional[dict] = None, **kwargs) -> Flask:
    """Create an app instance of the labbase2 application.

    Parameters
    ----------
    config : Optional[Union[str, Path]]
        A filename pointing to the configuration file. File has to be in JSON format.
        Filename is supposed to be relative to the instance path.
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
            if (permission := Permission.query.get(name)) is None:
                db.session.add(Permission(name=name, description=description))
            else:
                permission.description = description
            db.session.commit()

    from labbase2.models import events

    # If no user with admin rights is in the database, create one.
    with app.app_context():
        first, last, email = app.config.get("USER")

        if User.query.count() == 0:
            app.logger.info("No user in database; create admin as specified in config.")
            admin = User(first_name=first, last_name=last, email=email, is_admin=True)
            admin.set_password("admin")
            admin.permissions = Permission.query.all()
            db.session.add(admin)
        elif User.query.filter(User.is_active, User.is_admin).count() == 0:
            app.logger.info(
                "No active user with admin rights; trying to re-activate admin specified in config."
            )
            admin = User.query.filter(User.email == email).first()
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
                admin.permissions = Permission.query.all()
                db.session.add(admin)

        db.session.commit()

    # Register login_manager with application.
    from labbase2.models.user import login_manager

    # Register extensions with app.
    login_manager.init_app(app)

    # Register blueprints with application.
    from labbase2.views import (
        antibodies,
        auth,
        base,
        batches,
        chemicals,
        comments,
        files,
        fly_stocks,
        imports,
        oligonucleotides,
        plasmids,
        requests,
    )

    app.register_blueprint(base.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(imports.bp)
    app.register_blueprint(chemicals.bp)
    app.register_blueprint(comments.bp)
    app.register_blueprint(files.bp)
    app.register_blueprint(fly_stocks.bp)
    app.register_blueprint(requests.bp)
    app.register_blueprint(batches.bp)
    app.register_blueprint(antibodies.bp)
    app.register_blueprint(plasmids.bp)
    app.register_blueprint(oligonucleotides.bp)

    # Add custom template filters to Jinja2.
    from labbase2.utils import template_filters

    app.jinja_env.filters["format_date"] = template_filters.format_date
    app.jinja_env.filters["format_datetime"] = template_filters.format_datetime
    app.jinja_env.globals["random_string"] = secrets.token_hex

    # Logs every `top-level`request, i.e., every request that was done by the user himself and not
    # requests to static resources.
    @app.before_request
    def log_request():
        if not request.path.startswith("/static"):
            app.logger.info(
                "%(method)-6s %(path)s", {"method": request.method, "path": request.url}
            )

    return app
