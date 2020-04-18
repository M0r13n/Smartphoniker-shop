"""
This is place for all admin views.
"""
from flask import redirect, url_for, request, flash
from flask_admin import expose, helpers, AdminIndexView
from flask_admin.contrib.sqla import ModelView as _ModelView
from flask_login import current_user, login_user, logout_user

from project.server import flask_admin as admin, db
from project.server.models import User, Customer
# Create customized model view class
from .forms import LoginForm


class ProtectedModelView(_ModelView):

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('admin.login_view', next=request.url))


class ProtectedIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(ProtectedIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            if user:
                login_user(user)
            else:
                flash("Invalid Credentials")

        if current_user.is_authenticated:
            return redirect(url_for('.index'))

        self._template_args['form'] = form
        return super(ProtectedIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        logout_user()
        return redirect(url_for('.index'))


# Register ModelViews

admin.add_view(ProtectedModelView(User, db.session))  # User
admin.add_view(ProtectedModelView(Customer, db.session))  # Customer
