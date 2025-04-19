import pytest
from labbase2 import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SERVER_NAME": "localhost",
        "USER": ["Raphael", "Schleutker", "test@test.de"]
    })

    yield app

@pytest.fixture
def client(app):
    return app.test_client()
