from celery import Celery
from flask_admin import Admin
from flask_bcrypt import Bcrypt
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# instantiate the extensions
login_manager = LoginManager()
bcrypt = Bcrypt()
toolbar = DebugToolbarExtension()
db = SQLAlchemy()
celery = Celery()
migrate = Migrate()
flask_admin = Admin(name='admin', base_template='admin/admin_master.html', template_mode='bootstrap3')
