# project/server/tests/test_main.py


class TestAdmin:
    def test_admin_config(self):
        from project.server import flask_admin
        assert flask_admin.base_template == "admin/admin_master.html"
        assert flask_admin.name == "admin"
        assert flask_admin.url == "/admin"

    def test_admin_views(self, app):
        # make sure all views are protected
        with app.app_context():
            from project.server import flask_admin
            from project.server.admin.views import ProtectedIndexView
            for view in filter(lambda x: type(x) != ProtectedIndexView, flask_admin._views):
                assert not view.is_accessible()

    def test_admin_is_active(self, testapp):
        response = testapp.get("/admin")
        assert response.status_code == 308

        # follow all redirects
        while response.status_code in (302, 308):
            response = response.follow()

        # Assert unauthorized users are redirected to the login page
        assert response.status_code == 200
        assert "Login" in response
        assert "Email" in response
        assert "Password" in response

    def test_admin_login_works(self, user, testapp):
        # Goes to homepage
        res = testapp.get("/admin/login/")
        form = res.forms[0]
        form["email"] = user.email
        form["password"] = "admin"
        # Submits
        res = form.submit().follow()
        # Assert Welcome page is shown
        assert "PricePicker Admin Dashboard" in res
        assert "Willkommen" in res
        assert "Log out" in res
        assert res.status_code == 200
