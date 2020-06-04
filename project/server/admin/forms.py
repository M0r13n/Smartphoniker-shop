from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import validators
from wtforms.fields import StringField, PasswordField, FileField

from project.server import db
from project.server.models import User


class LoginForm(FlaskForm):
    email = StringField(
        validators=[
            validators.required(),
            validators.Email()
        ]
    )
    password = PasswordField(validators=[validators.required()])

    def validate_email(self, field):
        user = self.get_user()
        if user is None or not user.verify_password(self.password.data):
            raise validators.ValidationError('Invalid credentials')

    def get_user(self) -> User:
        return db.session.query(User).filter_by(email=self.email.data, admin=True).first()


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(
        validators=[
            validators.required()
        ]
    )
    new_password = PasswordField(
        "New Password",
        validators=[
            validators.required(),
            validators.Length(min=8, message="You need at least 8 characters"),
            validators.EqualTo('new_password_confirmation', message='Passwords must match')
        ]
    )
    new_password_confirmation = PasswordField("Confirm Password")

    def validate_old_password(self, field):
        if not current_user.verify_password(field.data):
            raise validators.ValidationError('Password is wrong')


class ImportRepairForm(FlaskForm):
    repair_file = FileField(
        validators=[
            FileRequired(),
            FileAllowed(['csv'], 'CSV only!')
        ]
    )
