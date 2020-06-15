from celery import Celery
from flask_admin import Admin
from flask_alchemydumps import AlchemyDumps
from flask_bcrypt import Bcrypt
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from project.common.redis import FlaskRedis
from project.common.tricoma_api import TricomaAPI
from project.common.tricoma_client import TricomaClient

# instantiate the extensions

login_manager = LoginManager()
bcrypt = Bcrypt()
alchemydumps = AlchemyDumps()
toolbar = DebugToolbarExtension()
db = SQLAlchemy()
celery = Celery()
migrate = Migrate()
flask_admin = Admin(name='admin', base_template='admin/admin_master.html', template_mode='bootstrap3')

redis_client = FlaskRedis()

tricoma_api = TricomaAPI()
tricoma_client = TricomaClient()
