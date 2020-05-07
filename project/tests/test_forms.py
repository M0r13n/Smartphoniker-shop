from flask_login import login_user

from project.server.admin.forms import LoginForm, ChangePasswordForm


class TestLoginForm:
    """Login form."""

    def test_validate_success(self, user):
        """Login successful."""
        form = LoginForm(email=user.email, password="admin")
        assert form.validate() is True

    def test_validate_unknown_username(self, db):
        """Unknown username."""
        form = LoginForm(email="unknown", password="example")
        assert form.validate() is False
        assert "Invalid credentials" in form.email.errors

    def test_validate_invalid_password(self, user):
        """Invalid password."""
        form = LoginForm(email=user.email, password="wrongpassword")
        assert form.validate() is False
        assert "Invalid credentials" in map(lambda x: x[0], form.errors.values())


class TestChangePasswordForm:
    """ Password Form"""

    def test_too_short(self, user, app):
        with app.app_context():
            login_user(user)
            form = ChangePasswordForm(old_password="admin", new_password="12345", new_password_confirmation="12345")
            assert not form.validate()
            assert not form.old_password.errors
            assert "You need at least 8 characters" in form.new_password.errors

    def test_wrong_old_pw(self, user, app):
        with app.app_context():
            login_user(user)
            form = ChangePasswordForm(old_password="wrong pw", new_password="123456789", new_password_confirmation="123456789")
            assert not form.validate()
            assert "Password is wrong" in form.old_password.errors
            assert not form.new_password.errors
            assert not form.new_password_confirmation.errors

    def test_pw_no_match(self, user, app):
        with app.app_context():
            login_user(user)
            form = ChangePasswordForm(old_password="admin", new_password="123456789", new_password_confirmation="bliblablub")
            assert not form.validate()
            assert "Passwords must match" in form.new_password.errors
            assert not form.old_password.errors
            assert not form.new_password_confirmation.errors

    def test_valid(self, app, user):
        with app.app_context():
            login_user(user)
            form = ChangePasswordForm(old_password="admin", new_password="123456789", new_password_confirmation="123456789")
            assert form.validate()
