# project/server/__init__.py


import os

import sentry_sdk
from flask import Flask, render_template
from sentry_sdk.integrations.flask import FlaskIntegration

from .extensions import login_manager, bcrypt, toolbar, db, migrate, flask_admin, celery, tricoma_client, tricoma_api, alchemydumps, redis_client


def create_app(script_info=None):
    # instantiate the app
    app = Flask(
        __name__,
        template_folder="../client/templates",
        static_folder="../client/static",
    )

    # set config
    app_settings = os.getenv(
        "APP_SETTINGS", "project.server.config.ProductionConfig"
    )
    app.config.from_object(app_settings)

    # set up extensions
    init_extensions(app)

    # setup admin after extensions are loaded
    init_admin(app)

    # Views
    init_blueprints(app)

    # error handlers
    @app.errorhandler(401)
    def unauthorized_page(error):
        return render_template("errors/401.html"), 401

    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("errors/500.html"), 500

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {"app": app, "db": db}

    return app


def init_extensions(app):
    login_manager.init_app(app)
    bcrypt.init_app(app)
    toolbar.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    tricoma_client.init_app(app)
    tricoma_api.init_app(app)
    init_login(app)
    init_celery(app)
    alchemydumps.init_app(app, db)
    redis_client.init_app(app)

    # finally set up sentry
    init_sentry(app)


def init_login(app):
    from project.server.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter(User.id == int(user_id)).first()


def init_blueprints(app):
    """ Register all blueprints"""
    # register blueprints
    from project.server.main.views import main_blueprint
    app.register_blueprint(main_blueprint)

    from project.server.main.sitemap import sitemap_blueprint
    app.register_blueprint(sitemap_blueprint)


def init_admin(app):
    """ Setup Flask-Admin"""
    from .admin.views import ProtectedIndexView
    flask_admin.init_app(app, url='/admin', index_view=ProtectedIndexView(name="Admin"))

    # Add the admin panel
    with app.app_context():
        pass


def init_celery(app=None):
    """ Setup celery with application factory """
    app = app or create_app()
    celery.conf.broker_url = app.config["CELERY_BROKER_URL"]
    celery.conf.result_backend = app.config["CELERY_RESULT_BACKEND"]
    # This is needed to fix the indefinite hang of delay and apply_async if celery is down
    celery.conf.broker_transport_options = {"max_retries": 2, "interval_start": 0, "interval_step": 0.2, "interval_max": 0.5}
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
