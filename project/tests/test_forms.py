from flask_login import login_user

from project.server.admin.forms import LoginForm, ChangePasswordForm
from project.server.main.forms import SelectRepairForm
from project.server.models import Repair


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


class TestSelectRepairForm:
    """ Test the repair form """

    def test_choices_single_repair(self, db, sample_device, sample_repair):
        """ Check that the choices are populated correctly"""
        repair_form = SelectRepairForm(sample_device)
        assert repair_form.repairs.choices == [(d.id, d) for d in sample_device.repairs]
        assert repair_form.color.choices == [(d.id, d) for d in sample_device.colors]
        assert len(repair_form.repairs.choices) == 1

    def test_choices_multiple_repairs(self, db, sample_device, sample_repair):
        """" Check that the choices are populated correctly"""
        Repair.create(name="Akku", price=123, device=sample_device)
        repair_form = SelectRepairForm(sample_device)
        assert repair_form.repairs.choices == [(d.id, d) for d in sample_device.repairs]
        assert repair_form.color.choices == [(d.id, d) for d in sample_device.colors]
        assert len(repair_form.repairs.choices) == 2

    def test_wrong_submit(self, db, sample_device, sample_repair):
        """ Check that invalid or malformed submits are handled"""
        repair_form = SelectRepairForm(sample_device)

        repair_form.color.data = None
        repair_form.repairs.data = None
        assert not repair_form.validate()

        repair_form.color.data = sample_device.colors[0].id
        repair_form.repairs.data = None
        assert not repair_form.validate()

        repair_form.color.data = None
        repair_form.repairs.data = [sample_repair.id]
        assert not repair_form.validate()

        # Malformed inputs
        repair_form.color.data = sample_device.colors[0].name
        assert not repair_form.validate()

        repair_form.repairs.data = [sample_repair.id]
        assert not repair_form.validate()

    def test_valid_submit_with_single_repair(self, db, sample_device, sample_repair):
        """ Check that invalid or malformed submits are handled"""
        repair_form = SelectRepairForm(sample_device)
        repair_form.color.data = sample_device.colors[0].id
        repair_form.repairs.data = [sample_repair.id]
        assert repair_form.validate()

    def test_valid_submit_with_multiple_repairs(self, db, sample_device, sample_repair):
        """ Check that invalid or malformed submits are handled"""
        another_repair = Repair.create(name="Akku", price=123, device=sample_device)
        repair_form = SelectRepairForm(sample_device)
        repair_form.color.data = sample_device.colors[0].id
        repair_form.repairs.data = [sample_repair.id, another_repair.id]
        assert repair_form.validate()
