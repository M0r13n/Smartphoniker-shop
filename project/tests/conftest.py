# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""

import logging

import pytest
from webtest import TestApp

from project.server import create_app
from project.server import db as _db
from project.server.models import User, Manufacturer, Color, Device, Customer, Shop


@pytest.fixture
def app():
    """Create application for the tests."""
    _app = create_app("tests.settings")
    _app.config.from_object("project.server.config.TestingConfig")
    _app.logger.setLevel(logging.CRITICAL)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture
def testapp(app):
    """Create Webtest app."""
    return TestApp(app)


@pytest.fixture
def prodapp(app):
    """Create a production app"""
    app.config.from_object("project.server.config.ProductionConfig")
    ctx = app.test_request_context()
    ctx.push()
    yield app
    ctx.pop()


@pytest.fixture
def devapp(app):
    """Create a dev app"""
    app.config.from_object("project.server.config.DevelopmentConfig")
    ctx = app.test_request_context()
    ctx.push()
    yield app
    ctx.pop()


@pytest.fixture
def db(app):
    """Create database for the tests."""
    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    # Explicitly close DB connection
    _db.session.close()
    _db.drop_all()


@pytest.fixture
def user(db):
    """Create user for the tests."""
    user = User.create(email="ad@min.com", password="admin", admin=True)
    return user


@pytest.fixture
def sample_manufacturer():
    """Create a sample manufacturer"""
    return Manufacturer.create(name="Apple")


@pytest.fixture
def sample_color():
    """Create a sample color"""
    return Color.create(name="Black", color_code="#000000")


@pytest.fixture
def sample_device(sample_manufacturer, sample_color):
    """ Create a sample device """
    return Device.create(name="iPhone 6S", colors=[sample_color], manufacturer=sample_manufacturer)


@pytest.fixture
def sample_customer():
    return Customer.create(first_name="Test", last_name="Kunde", street="Eine Straße 1", zip_code="11233", city="Kiel", tel="+49 113455665 45", email="leon.morten@gmail.com")


@pytest.fixture
def sample_shop():
    return Shop.create(name="Zentrale")
