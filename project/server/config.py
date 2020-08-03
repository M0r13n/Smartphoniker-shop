# project/server/config.py

import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

dotenv_path = os.path.join(os.path.dirname(__file__), '../../.local_env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


class BaseConfig(object):
    """Base configuration."""

    APP_NAME = os.getenv("APP_NAME", "PricePicker-v2")
    BCRYPT_LOG_ROUNDS = 8
    SECRET_KEY = os.getenv("SECRET_KEY", "my_precious")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SENTRY_DSN = os.getenv("SENTRY_DSN")
    # set optional bootswatch theme
    # FLASK_ADMIN_SWATCH = 'Cyborg'
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND_URL", REDIS_URL)

    # Tricoma stuff
    TRICOMA_BASE_URL = os.getenv("TRICOMA_BASE_URL")
    TRICOMA_USERNAME = os.getenv("TRICOMA_USERNAME")
    TRICOMA_PASSWORD = os.getenv("TRICOMA_PASSWORD")
    TRICOMA_API_URL = os.getenv("TRICOMA_API_URL")
    REGISTER_CUSTOMER_IN_TRICOMA = os.getenv("REGISTER_CUSTOMER_IN_TRICOMA", False)

    # Mail
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS")
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME)
    MAIL_PORT = os.getenv("MAIL_PORT")

    NOTIFICATION_MAILS = ['support@smartphoniker.de', 'leonrichter1337@gmail.com']
    # NOTIFICATION_MAILS = ['leonrichter1337@gmail.com']

    # Vigil
    VIGIL_URL = os.getenv("VIGIL_URL")
    VIGIL_TOKEN = os.getenv("VIGIL_TOKEN")
    VIGIL_PROBE_ID = os.getenv("VIGIL_PROBE_ID")
    VIGIL_NODE_ID = os.getenv("VIGIL_NODE_ID")
    VIGIL_REPLICA_ID = os.getenv("VIGIL_REPLICA_ID")
    VIGIL_INTERVAL = int(os.getenv("VIGIL_INTERVAL", "0"))

    # Affiliate Bonus
    AFFILIATE_BONUS = os.getenv("AFFILIATE_BONUS", 10.0)

    # Proxy Fix
    PROXY_FIX_NUM = os.getenv("PROXY_FIX_NUM", 0)

    # Cacheing

    CACHE_TYPE = os.getenv("CACHE_TYPE", "simple")
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_REDIS_URL = os.getenv("CACHE_REDIS_URL", REDIS_URL)


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    FLASK_DEBUG = True
    DEBUG = True
    DEBUG_TB_ENABLED = True
    WTF_CSRF_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")


class TestingConfig(BaseConfig):
    """Testing configuration."""
    FLASK_DEBUG = False
    DEBUG = False
    DEBUG_TB_ENABLED = False
    WTF_CSRF_ENABLED = False

    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_TEST_URL", "postgresql://postgres:postgres@127.0.0.1/pricepicker")
    TESTING = True


class ProductionConfig(BaseConfig):
    """Production configuration."""
    FLASK_DEBUG = False
    DEBUG = False
    DEBUG_TB_ENABLED = False
    WTF_CSRF_ENABLED = True
    TESTING = False
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")


RAIDER_CONFIG = dict(
    host=os.getenv("RAIDER_TRACKING_HOST", "affiliates.smartphoniker.shop"),
    track_token=os.getenv("RAIDER_TRACK_TOKEN", "YOUR_SECRET_TOKEN"),
    default_currency=os.getenv("RAIDER_CURRENCY", "EUR"),
)
