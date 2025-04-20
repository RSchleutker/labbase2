from flask import url_for
from flask_login import current_user, login_user
from sqlalchemy import select, func
from labbase2 import models
from labbase2.models import db


def test_login_get(app, client):
    with app.app_context(), client:
        url = url_for("auth.login")
        response = client.get(url)

    assert response.status_code == 200
    assert b"Sign in" in response.data


def test_login_with_wrong_user(app, client):
    with app.app_context(), client:
        url = url_for("auth.login")
        response = client.post(
            url,
            data={"email": "wrong_email@test.de", "password": "admin", "submit": True},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Invalid email address or username!" in response.data
        assert current_user.is_anonymous
        assert not current_user.is_authenticated


def test_login_with_wrong_pw(app, client):
    with app.app_context(), client:
        url = url_for("auth.login")
        response = client.post(
            url,
            data={"email": "test@test.de", "password": "wrong_pw", "submit": True},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Wrong password!" in response.data
        assert current_user.is_anonymous
        assert not current_user.is_authenticated


def test_login_inactive_user(app, client):
    with app.app_context(), client:
        user = db.session.get(models.User, 1)
        user.is_active = False

        db.session.commit()

        url = url_for("auth.login")
        response = client.post(
            url,
            data={"email": "test@test.de", "password": "admin", "submit": True},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Your account is inactive!" in response.data
        assert current_user.is_anonymous
        assert not current_user.is_authenticated


def test_login_with_correct_data(app, client):
    with app.app_context(), client:
        url = url_for("auth.login")
        response = client.post(
            url,
            data={"email": "test@test.de", "password": "admin", "submit": True},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Successfully logged in!" in response.data
        assert not current_user.is_anonymous
        assert current_user.is_authenticated
        assert current_user.username == "Max Mustermann"


def test_logout_user(app, client):
    with app.app_context(), app.test_request_context(), client:
        url = url_for("auth.logout")
        user = db.session.get(models.User, 1)
        login_user(user)
        response = client.get(url, follow_redirects=True)

        assert b"Successfully logged out!" in response.data
        assert current_user.is_anonymous
        assert not current_user.is_authenticated


def test_register_existing_email(app, client):
    with app.app_context(), app.test_request_context(), client:
        admin = db.session.get(models.User, 1)
        login_user(admin)

        url = url_for("auth.register")
        response = client.post(
            url,
            data={
                "first_name": "Maja",
                "last_name": "Musterfrau",
                "email": "test@test.de",
                "password": "This_isAPassword123",
                "password2": "This_isAPassword123",
                "submit": True,
            },
            follow_redirects=True,
        )

        user_count = db.session.scalar(select(func.count()).select_from(models.User))

        assert b"Email address already exists!" in response.data
        assert user_count == 1


def test_register_new_user(app, client):
    with app.app_context(), app.test_request_context(), client:
        admin = db.session.get(models.User, 1)
        login_user(admin)

        url = url_for("auth.register")
        response = client.post(
            url,
            data={
                "first_name": "Maja",
                "last_name": "Musterfrau",
                "email": "test2@test.de",
                "password": "This_isAPassword123",
                "password2": "This_isAPassword123",
                "submit": True,
            },
            follow_redirects=True,
        )

        user_count = db.session.scalar(select(func.count()).select_from(models.User))

        assert b"Successfully registered new user!" in response.data
        assert user_count == 2
