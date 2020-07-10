from flask import Blueprint, send_from_directory, request
from flask_sitemap import Sitemap


class SitemapBlueprint(Blueprint):
    """
    Contains all the logic for generating a sitemap.xml
    """
    STATIC_ROUTES = [
        'shop_blueprint.home',
        'shop_blueprint.manufacturer',
        'shop_blueprint.agb',
        'shop_blueprint.datenschutz',
        'shop_blueprint.faq',
        'shop_blueprint.impressum',
        'shop_blueprint.references',
    ]

    OTHER_ROUTES = [
        ('shop_blueprint.series', {'manufacturer_name': 'Apple'}),
        ('shop_blueprint.series', {'manufacturer_name': 'Samsung'}),
        ('shop_blueprint.series', {'manufacturer_name': 'Huawei'}),
    ]

    def register(self, app, options, first_registration=False):
        sitemap = Sitemap(app=app)

        @app.route('/robots.txt')
        def static_from_root():
            return send_from_directory(app.static_folder, request.path[1:])

        @sitemap.register_generator
        def index():
            # all routes without params
            for route in self.STATIC_ROUTES:
                # (route, options, lastmod, changefreq, priority)
                yield route, {}

            for route, params in self.OTHER_ROUTES:
                yield route, params


sitemap_blueprint = SitemapBlueprint('sitemap', __name__)
