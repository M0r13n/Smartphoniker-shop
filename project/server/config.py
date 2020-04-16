# project/server/config.py

import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


class BaseConfig(object):
    """Base configuration."""

    APP_NAME = os.getenv("APP_NAME", "PricePicker-v2")
    BCRYPT_LOG_ROUNDS = 8
    SECRET_KEY = os.getenv("SECRET_KEY", "my_precious")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # set optional bootswatch theme
    FLASK_ADMIN_SWATCH = 'Cyborg'


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    FLASK_DEBUG = True
    DEBUG = True
    DEBUG_TB_ENABLED = True
    WTF_CSRF_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///{0}".format(os.path.join(basedir, "dev.db"))
    )


class TestingConfig(BaseConfig):
    """Testing configuration."""
    FLASK_DEBUG = False
    DEBUG = False
    DEBUG_TB_ENABLED = False
    WTF_CSRF_ENABLED = False

    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_TEST_URL", "sqlite:///")
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
