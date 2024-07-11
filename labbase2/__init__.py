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
    from labbase2.models import User, UserRole
    from labbase2.models.user import login_manager

    # Register extensions with app.
    db.init_app(app)
    login_manager.init_app(app)
    moment = Moment(app)

    with app.app_context():
        # Create database and add tables (if not yet present).
        db.create_all()

        # Add default roles to database.
        for role in app.config['USER_ROLES']:
            if not UserRole.query.filter_by(name=role).first():
                db.session.add(UserRole(name=role))
                db.session.commit()

        # Add the 'admin' user.
        if not User.query.first():
            admin = User(username="admin", email=app.config.get("EMAIL"))
            admin.set_password("admin")
            admin.roles.append(UserRole.query.filter_by(name="admin").first())
            db.session.add(admin)
            db.session.commit()

            print("A user 'admin' with password 'admin' was created. Please log in and change the password ASAP.")

    from labbase2.views import base
    from labbase2.views import auth
    from labbase2.views import imports
    from labbase2.views import comments
    from labbase2.views import files
    from labbase2.views import requests
    from labbase2.views import batches
    from labbase2.views import antibodies
    from labbase2.views.antibodies import dilutions
    from labbase2.views import oligonucleotides

    app.register_blueprint(base.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(imports.bp)
    app.register_blueprint(comments.bp)
    app.register_blueprint(files.bp)
    app.register_blueprint(requests.bp)
    app.register_blueprint(batches.bp)
    app.register_blueprint(antibodies.bp)
    app.register_blueprint(dilutions.bp)
    app.register_blueprint(oligonucleotides.bp)

    from labbase2.utils.template_filters import format_date
    from labbase2.utils.template_filters import format_datetime

    app.jinja_env.filters['format_date'] = format_date
    app.jinja_env.filters['format_datetime'] = format_datetime

    return app
