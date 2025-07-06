import pytest

from labbase2 import create_app
from labbase2.database import db
from labbase2.models import Group, User


@pytest.fixture
def app():
    app = create_app(
        config_dict={
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "SERVER_NAME": "localhost",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "USER": ["Max", "Mustermann", "test@test.de"],
        }
    )

    yield app


@pytest.fixture
def client(app):
    return app.test_client()
