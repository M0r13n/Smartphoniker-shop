from project.server.admin.forms import LoginForm


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
