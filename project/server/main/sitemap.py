from flask import Blueprint, send_from_directory, request
from flask_sitemap import Sitemap

from project.server.models import Manufacturer


class SitemapBlueprint(Blueprint):
    """
    Contains all the logic for generating a sitemap.xml
    """
    STATIC_ROUTES = [
        'main.home',
        'main.manufacturer',
        'main.agb',
        'main.datenschutz',
        'main.faq',
        'main.impressum',
        'main.references',
    ]

    OTHER_ROUTES = [
        ('main.series', {'manufacturer_name': 'Apple'}),
        ('main.series', {'manufacturer_name': 'Samsung'}),
        ('main.series', {'manufacturer_name': 'Huawei'}),
        ('main.series', {'manufacturer_name': 'Sony'}),
        ('main.series', {'manufacturer_name': 'Google'}),
        ('main.series', {'manufacturer_name': 'Xiaomi'}),
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

            # models
            all_manufacturers: [Manufacturer] = Manufacturer.query.filter(Manufacturer.activated == True).all()  # noqa
            for manufacturer in all_manufacturers:
                for series in manufacturer.series:
                    for device in series.devices:
                        # last_updated = datetime.fromtimestamp(brigade['properties']['last_updated'])
                        params = {
                            'manufacturer_name': manufacturer.name,
                            'series_name': series.name,
                            'device_name': device.name,

                        }
                        yield 'main.model', params


sitemap_blueprint = SitemapBlueprint('sitemap', __name__)
