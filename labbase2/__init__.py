from flask import Flask
from flask_moment import Moment
from pathlib import Path
import tomllib


def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_file(config_filename, load=tomllib.load, text=False)

    # Check if upload folder exists and create if necessary.
    upload_folder = Path(app.instance_path, app.config["UPLOAD_FOLDER"])
    upload_folder.mkdir(parents=True, exist_ok=True)

    from labbase2.models import db
    from labbase2.models import User, Permission
    from labbase2.models.user import login_manager

    # Register extensions with app.
    db.init_app(app)
    login_manager.init_app(app)
    moment = Moment(app)

    with app.app_context():
        # Create database and add tables (if not yet present).
        db.create_all()

        # Add permissions to database.
        for name, description in app.config.get("PERMISSIONS"):
            permission = Permission.query.get(name)
            if permission is None:
                db.session.add(Permission(name=name, description=description))
            else:
                permission.description = description
            db.session.commit()

        # Add the 'admin' user.
        if not User.query.first():
            first, last, email = app.config.get("USER")
            admin = User(first_name=first, last_name=last, email=email, is_admin=True)
            admin.set_password("admin")
            admin.permissions = Permission.query.all()

            db.session.add(admin)
            db.session.commit()

    from labbase2.views import base
    from labbase2.views import auth
    from labbase2.views import imports
    from labbase2.views import comments
    from labbase2.views import files
    from labbase2.views import requests
    from labbase2.views import batches
    from labbase2.views import antibodies
    from labbase2.views import plasmids
    from labbase2.views import oligonucleotides

    app.register_blueprint(base.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(imports.bp)
    app.register_blueprint(comments.bp)
    app.register_blueprint(files.bp)
    app.register_blueprint(requests.bp)
    app.register_blueprint(batches.bp)
    app.register_blueprint(antibodies.bp)
    app.register_blueprint(plasmids.bp)
    app.register_blueprint(oligonucleotides.bp)

    from labbase2.utils.template_filters import format_date
    from labbase2.utils.template_filters import format_datetime
    from labbase2.utils.template_filters import user_has_permission

    app.jinja_env.filters["format_date"] = format_date
    app.jinja_env.filters["format_datetime"] = format_datetime
    app.jinja_env.globals.update(user_has_permission=user_has_permission)

    return app
