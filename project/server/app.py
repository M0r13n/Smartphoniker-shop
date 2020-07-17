# project/server/__init__.py


import os

from flask import Flask, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

from .extensions import db, flask_admin, init_extensions


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

    apply_proxy_fix(app)
    return app


def apply_proxy_fix(app):
    num_proxies = app.config.get('PROXY_FIX_NUM')
    if num_proxies:
        app.wsgi_app = ProxyFix(app.wsgi_app, num_proxies)
    app.logger.info(f"App configured to use {num_proxies} proxies")


def init_blueprints(app):
    """ Register all blueprints"""
    # register blueprints
    from project.server.shop.views import main_blueprint
    app.register_blueprint(main_blueprint)

    from project.server.shop.sitemap import sitemap_blueprint
    app.register_blueprint(sitemap_blueprint)

    from project.server.health.views import health_bp
    app.register_blueprint(health_bp)


def init_admin(app):
    """ Setup Flask-Admin"""
    from .admin.views import ProtectedIndexView
    flask_admin.init_app(app, url='/admin', index_view=ProtectedIndexView(name="Admin"))

    # Add the admin panel
    with app.app_context():
        pass
