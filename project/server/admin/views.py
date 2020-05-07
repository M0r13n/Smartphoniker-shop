"""
This is place for all admin views.
"""
from flask import redirect, url_for, request, flash, abort
from flask_admin import expose, helpers, AdminIndexView
from flask_admin.contrib.sqla import ModelView as _ModelView
from flask_login import current_user, login_user, logout_user

from project.server import flask_admin as admin, db
from project.server.models import User, Customer, MailLog, Shop, Order, Device, Manufacturer, Repair, Image, DeviceSeries
# Create customized model view class
from .forms import LoginForm, ChangePasswordForm
from ..models.device import Color


class ProtectedModelView(_ModelView):

    def is_accessible(self):
        """ All admin views require authentication """
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        """
        Redirect to login page if user doesn't have access
        """
        return redirect(url_for('admin.login_view', next=request.url))

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(403)
            else:
                return redirect(url_for('admin.login_view', next=request.url))


class ProtectedIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        """ Render the welcome page for the admin """
        if not current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(ProtectedIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        """ Logic to handle a user logging in """
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

    @expose('/password/', methods=('GET', 'POST'))
    def change_password_view(self):
        """ Logic for updating a password """
        if not current_user.is_authenticated:
            abort(403)

        form = ChangePasswordForm(request.form)
        if helpers.validate_form_on_submit(form):
            current_user.password = form.new_password.data
            current_user.save()
            logout_user()
            flash("Password updated successfully. Please login again.", "success")
            return redirect(url_for('.login_view'))

        self._template_args['form'] = form
        return self.render('admin/password.html')

    @expose('/logout/')
    def logout_view(self):
        """ Logout """
        logout_user()
        return redirect(url_for('.index'))


# Register ModelViews

admin.add_view(ProtectedModelView(User, db.session))  # User
admin.add_view(ProtectedModelView(Customer, db.session))  # Customer
admin.add_view(ProtectedModelView(MailLog, db.session))  # Mails
admin.add_view(ProtectedModelView(Shop, db.session))  # Shop
admin.add_view(ProtectedModelView(Order, db.session))  # Orders
admin.add_view(ProtectedModelView(Device, db.session))  # Devices
admin.add_view(ProtectedModelView(Color, db.session))  # Colors
admin.add_view(ProtectedModelView(Manufacturer, db.session))  # Manufacturers
admin.add_view(ProtectedModelView(DeviceSeries, db.session))  # Manufacturers
admin.add_view(ProtectedModelView(Repair, db.session))  # Repairs
admin.add_view(ProtectedModelView(Image, db.session))  # Images
