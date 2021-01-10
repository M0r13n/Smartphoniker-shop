# project/server/tests/test_main.py
import csv

from flask import url_for
from webtest import AppError

from project.server.models import Repair
from project.tests.utils import login


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
        assert response.status_code in (308, 302)

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

    def test_admin_login_shortcut(self, user, testapp):
        response = login(testapp, user.email, "admin")
        assert "Hier kannst du alle nötigen Einstellungen vornehmen und Geräte, sowie Reparaturen anlegen.".encode(
            'utf-8') in response

    def test_admin_change_pw_protected(self, testapp):
        try:
            res = testapp.get(url_for('admin.change_password_view')).follow()
            assert res.status_code == 403
        except AppError as e:
            assert "Bad response: 403 FORBIDDEN" in str(e)

    def test_that_every_page_at_least_loads(self, user, some_devices, db, testapp):
        res = testapp.get("/admin/login/")
        form = res.forms[0]
        form["email"] = user.email
        form["password"] = "admin"
        res = form.submit().follow()

        endpoints = (
            'customer.index_view',
            'pending.index_view',
            'orders.index_view',
            'manufacturer.index_view',
            'deviceseries.index_view',
            'device.index_view',
            'shop.index_view',
            'repair.index_view',
            'image.index_view'
        )

        for endpoint in endpoints:
            url = url_for(endpoint)
            response = testapp.get(url)
            assert response.status_code == 200

    def test_export(self, user, sample_repair, another_repair, db, testapp):
        login(testapp, user.email, "admin")
        response = testapp.get("http://localhost:5000/admin/repair/export/csv/")
        cr = csv.reader(response.text.splitlines(), delimiter=',')

        result = list(cr)

        assert len(result) == Repair.query.count() + 1

        for repair in Repair.query.all():
            assert [
                       repair.device.manufacturer.name,
                       repair.device.series.name,
                       repair.device.name,
                       repair.name,
                       "".join(color.name for color in repair.device.colors),
                       str(repair.price)
                   ] in result
