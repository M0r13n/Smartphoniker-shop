from flask import Response, Flask


def _try_auth(client, user) -> Response:
    response: Response = client.post("/admin/login/", data=dict(email=user.email, password="admin"))
    return response


class TestAdminCsrf:

    def test_test_client_has_csrf_deactivated(self, app: Flask, db, user):
        response = _try_auth(app.test_client(), user)
        assert response.status_code == 302  # 302 means the login succeeded and the user is redirected to admin welcome page
        assert b"The CSRF token is missing." not in response.data

    def test_login_is_csrf_protected(self, prodapp: Flask, db, user):
        response = _try_auth(prodapp.test_client(), user)
        assert response.status_code == 200  # 200 means that the same page was returned -> auth failed
        assert b"The CSRF token is missing." in response.data
