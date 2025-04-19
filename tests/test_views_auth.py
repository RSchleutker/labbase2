from flask import url_for


def test_login_get(app, client):
    with app.app_context():
        url = url_for("auth.login")
        response = client.get(url)

    assert response.status_code == 200
    assert b"Sign in" in response.data