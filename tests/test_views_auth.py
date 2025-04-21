from http.client import responses

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


def test_get_edit_user(app, client):
    with app.app_context(), app.test_request_context(), client:
        user = db.session.get(models.User, 1)
        login_user(user)
        url = url_for("auth.edit_user")
        response = client.get(url)

        assert response.status_code == 200
        assert b"Edit Profile" in response.data


def test_edit_user_with_wrong_pw(app, client):
    with app.app_context(), app.test_request_context(), client:
        user = db.session.get(models.User, 1)
        login_user(user)
        url = url_for("auth.edit_user")
        response = client.post(
            url,
            data={
                "first_name": "Maximilian",
                "last_name": "Mustermann",
                "email": "test@test.de",
                "timezone": "UTC",
                "password": "wrong_password",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Password is incorrect!" in response.data
        assert user.first_name == "Max"


def test_edit_user(app, client):
    with app.app_context(), app.test_request_context(), client:
        user = db.session.get(models.User, 1)
        login_user(user)
        url = url_for("auth.edit_user")
        response = client.post(
            url,
            data={
                "first_name": "Maximilian",
                "last_name": "Mustermann",
                "email": "test@test.de",
                "timezone": "UTC",
                "password": "admin",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Successfully edited user profile!" in response.data
        assert user.first_name == "Maximilian"


def test_remove_only_admin(app, client):
    with app.app_context(), app.test_request_context(), client:
        user = db.session.get(models.User, 1)
        login_user(user)
        url = url_for("auth.change_admin_status", id_=1)
        response = client.get(url, follow_redirects=True)

        assert response.status_code == 200
        assert b"Successfully changed admin setting for" in response.data
        assert b"No user with admin rights! Reverting previous change!" in response.data
        assert user.is_admin


def test_make_user_admin(app, client):
    with app.app_context(), app.test_request_context(), client:
        admin = db.session.get(models.User, 1)
        user = models.User(first_name="Maja", last_name="Musterfrau", email="test2@test.de")
        user.set_password("TestPassword")
        db.session.add(user)
        db.session.commit()

        login_user(admin)
        url = url_for("auth.change_admin_status", id_=2)
        response = client.get(url, follow_redirects=True)

        assert response.status_code == 200
        assert b"Successfully changed admin setting for" in response.data
        assert b"No user with admin rights! Reverting previous change!" not in response.data
        assert user.is_admin


def test_remove_admin_from_user(app, client):
    with app.app_context(), app.test_request_context(), client:
        admin = db.session.get(models.User, 1)
        user = models.User(first_name="Maja", last_name="Musterfrau", email="test2@test.de")
        user.is_admin = True
        user.set_password("TestPassword")
        db.session.add(user)
        db.session.commit()

        login_user(admin)
        url = url_for("auth.change_admin_status", id_=2)
        response = client.get(url, follow_redirects=True)

        assert response.status_code == 200
        assert b"Successfully changed admin setting for" in response.data
        assert b"No user with admin rights! Reverting previous change!" not in response.data
        assert not user.is_admin


# TODO Test auth.change_password
# TODO Test auth.change_permissions
# TODO Test auth.change_active_status


def test_inactivate_only_admin(app, client):
    with app.app_context(), app.test_request_context(), client:
        admin = db.session.get(models.User, 1)
        login_user(admin)

        assert admin.is_active

        url = url_for("auth.change_active_status", id_=1)
        response = client.get(url, follow_redirects=True)

        assert response.status_code == 200
        assert b"Successfully changed active setting for" in response.data
        assert b"No active user! Reverting previous change!" in response.data
        assert admin.is_active


def test_inactivate_user(app, client):
    with app.app_context(), app.test_request_context(), client:
        admin = db.session.get(models.User, 1)
        user = models.User(first_name="Maja", last_name="Musterfrau", email="test2@test.de")
        user.set_password("TestPassword")
        db.session.add(user)
        db.session.commit()

        login_user(admin)

        assert user.is_active

        url = url_for("auth.change_active_status", id_=2)
        response = client.get(url, follow_redirects=True)

        assert response.status_code == 200
        assert b"Successfully changed active setting for" in response.data
        assert not user.is_active


# TODO Test auth.create_password_reset


def test_users_get(app, client):
    with app.app_context(), app.test_request_context(), client:
        url = url_for("auth.users")

        admin = db.session.get(models.User, 1)
        login_user(admin)

        response = client.get(url)

        assert response.status_code == 200
        assert b"Mustermann" in response.data
        assert b"Musterfrau" not in response.data

        user = models.User(first_name="Maja", last_name="Musterfrau", email="test2@test.de")
        user.set_password("TestPassword")
        db.session.add(user)
        db.session.commit()

        response = client.get(url)

        assert response.status_code == 200
        assert b"Mustermann" in response.data
        assert b"Musterfrau" in response.data
