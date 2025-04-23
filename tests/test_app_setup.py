from labbase2 import models
from labbase2.models import db
from sqlalchemy import select, func


def test_first_user_is_admin_and_active(app):
    with app.app_context():
        user = db.session.get(models.User, 1)

        assert user is not None
        assert user.is_admin
        assert user.is_active
        assert user.first_name == "Max"
        assert user.last_name == "Mustermann"
        assert user.email == "test@test.de"


def test_all_permissions_in_db(app):
    with app.app_context():
        permissions_count = db.session.scalar(select(func.count()).select_from(models.Permission))

    assert permissions_count == len(app.config["PERMISSIONS"])


def test_first_user_has_all_permissions(app):
    with app.app_context():
        permissions = db.session.scalars(select(models.Permission)).all()
        user = db.session.get(models.User, 1)

    assert len(permissions) == len(app.config["PERMISSIONS"])
    assert set(user.permissions) == set(permissions)
