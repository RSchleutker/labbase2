import pytest
from labbase2 import create_app


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
