# project/server/tests/test_config.py


class TestTestingConfig:
    def test_app_is_testing(self, app):
        assert app
        assert not app.config['FLASK_DEBUG']
        assert not app.config['DEBUG']
        assert not app.config['DEBUG_TB_ENABLED']
        assert not app.config['WTF_CSRF_ENABLED']
        assert app.config['TESTING']


class TestProductionConfig:

    def test_app_is_production(self, app_prod):
        assert app_prod
        assert not app_prod.config['FLASK_DEBUG']
        assert not app_prod.config['DEBUG']
        assert not app_prod.config['DEBUG_TB_ENABLED']
        assert app_prod.config['WTF_CSRF_ENABLED']
        assert not app_prod.config['TESTING']


class TestDevelopmentConfig:
    def test_app_is_dev(self, devapp):
        assert devapp
        assert devapp.config['FLASK_DEBUG']
        assert devapp.config['DEBUG']
        assert devapp.config['DEBUG_TB_ENABLED']
        assert devapp.config['WTF_CSRF_ENABLED']
        assert not devapp.config['TESTING']
