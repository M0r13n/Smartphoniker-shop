import sentry_sdk
from celery import Celery
from flask_admin import Admin
from flask_alchemydumps import AlchemyDumps
from flask_bcrypt import Bcrypt
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from raider_reporter.reporter import RaiderReporter
from sentry_sdk.integrations.flask import FlaskIntegration
from vigil_reporter.reporter import VigilReporter, RequestFailedError

from project.server.common.redis import FlaskRedis
from project.server.common.tricoma_api import TricomaAPI
from project.server.common.tricoma_client import TricomaClient
# instantiate the extensions
from project.server.config import TALISMAN_CONFIG, RAIDER_CONFIG

login_manager = LoginManager()
bcrypt = Bcrypt()
alchemydumps = AlchemyDumps()
toolbar = DebugToolbarExtension()
db = SQLAlchemy()
celery = Celery()
migrate = Migrate()
flask_admin = Admin(name='admin', base_template='admin/admin_master.html', template_mode='bootstrap3')

talisman = Talisman()

redis_client = FlaskRedis()

tricoma_api = TricomaAPI()
tricoma_client = TricomaClient()

raider = RaiderReporter.from_config(RAIDER_CONFIG)


def init_talisman(app):
    talisman.init_app(app, **TALISMAN_CONFIG)


def init_login(app):
    from project.server.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter(User.id == int(user_id)).first()


def init_celery(app=None):
    """ Setup celery with application factory """
    if app is None:
        from project.server import create_app
        app = create_app()
    celery.conf.broker_url = app.config["CELERY_BROKER_URL"]
    celery.conf.result_backend = app.config["CELERY_RESULT_BACKEND"]
    celery.conf.redis_socket_timeout = 2.0
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context"""

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def init_sentry(app):
    """ Enable remote logging to Sentry.io"""
    if app.config.get('SENTRY_DSN'):
        # Only init sentry if the DSN is set in the current environment
        sentry_sdk.init(
            app.config.get('SENTRY_DSN'),
            integrations=[
                FlaskIntegration()
            ]
        )


def start_vigil_reporter(app):
    """
    This should be called AFTER the app has been fully loaded!
    Otherwise it might prevent the shop thread from stopping.
    """
    conf = app.config
    vigil_config = dict(
        url=conf['VIGIL_URL'],
        token=conf['VIGIL_TOKEN'],
        probe_id=conf['VIGIL_PROBE_ID'],
        node_id=conf['VIGIL_NODE_ID'],
        replica_id=conf['VIGIL_REPLICA_ID'],
        interval=conf['VIGIL_INTERVAL']
    )

    def start():
        try:
            reporter = VigilReporter.from_config(vigil_config)
            reporter.start_reporting()
        except ValueError as e:
            # Vigil en vars not set
            app.logger.warning("Vigil Reporter not set up, because %s" % str(e))
        except RequestFailedError as e:
            app.logger.error(e)

    app.before_first_request(start)


def init_sqlalchemy(app):
    db.init_app(app)
    from project.server.models.crud import CRUDMixin
    CRUDMixin.set_session(db.session)


def init_extensions(app):
    login_manager.init_app(app)
    bcrypt.init_app(app)
    toolbar.init_app(app)
    init_sqlalchemy(app)
    migrate.init_app(app, db)
    tricoma_client.init_app(app)
    tricoma_api.init_app(app)
    init_login(app)
    init_celery(app)
    alchemydumps.init_app(app, db)
    redis_client.init_app(app)
    init_talisman(app)
    start_vigil_reporter(app)

    # finally set up sentry
    init_sentry(app)
