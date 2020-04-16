from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField
from wtforms import validators

from project.server import db
from project.server.models import User


class LoginForm(FlaskForm):
    email = StringField(validators=[validators.required(), validators.Email()])
    password = PasswordField(validators=[validators.required()])

    def validate_email(self, field):
        user = self.get_user()
        if user is None or not user.verify_password(self.password.data):
            raise validators.ValidationError('Invalid credentials')

    def get_user(self) -> User:
        return db.session.query(User).filter_by(email=self.email.data, admin=True).first()
