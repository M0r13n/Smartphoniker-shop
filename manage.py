# manage.py
import os
import subprocess
import sys

import click
import coverage
from flask.cli import FlaskGroup

from project.server.app import create_app, db
from project.server.models import User, Shop, Customer, Manufacturer
from project.server.models.device import Color, Device

app = create_app()
cli = FlaskGroup(create_app=create_app)

HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(HERE, "project")
TEST_PATH = os.path.join(PROJECT_ROOT, "tests")

# code coverage
COV = coverage.coverage(
    branch=True,
    include="project/*",
    omit=[
        "project/tests/*",
        "project/server/config.py",
        "project/server/*/__init__.py",
    ],
)
COV.start()


def create_sample_data():
    Shop.create(name="Zentrale")
    Shop.create(name="Kiel")
    Shop.create(name="Schwentinental")
    Shop.create(name="Itzehoe")
    Shop.create(name="Lübeck")
    Shop.create(name="Rendsburg")
    Customer.create(first_name="Test", last_name="Kunde", street="Eine Straße 1", zip_code="11233", city="Kiel", tel="+49 113455665 45", email="leon.morten@gmail.com")
    b = Color.create(name="Black", color_code="#000000")
    w = Color.create(name="White", color_code="#FFFFFF")
    a = Manufacturer.create(name="Apple")
    Device.create(name="iPhone 6S", colors=[b, w], manufacturer=a)
    Device.create(name="iPhone 7", colors=[b, w], manufacturer=a)
    User.create(email="ad@min.com", password="admin", admin=True)


@cli.command()
def create_db():
    """ Drops all existing tables and creates them afterwards """
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command()
def dev_db():
    """Restore a clean DB with sample Data"""
    db.drop_all()
    db.create_all()
    create_sample_data()
    db.session.commit()


@cli.command()
def drop_db():
    """Drops the db tables."""
    db.drop_all()


@cli.command()
def create_admin():
    """Creates the admin user."""
    User.create(email="ad@min.com", password="admin", admin=True)


@cli.command()
def create_data():
    """Creates sample data."""
    create_sample_data()


@cli.command()
def clean_db():
    """ Restore a clean working state """
    db.drop_all()
    db.create_all()
    db.session.commit()
    User.create(email="ad@min.com", password="admin", admin=True)
    create_sample_data()


@cli.command()
@click.argument("loglevel",
                default="info",
                required=True,
                type=click.Choice(['error', 'warning', 'info', 'debug'],
                                  case_sensitive=False))
def start_worker(loglevel):
    """
    Starts celery worker
    """
    # celery worker -A myapi.celery_app:app --loglevel=info
    import subprocess
    subprocess.run(["celery", "worker", "-A", "project.server.celery_app:app", f"--loglevel={loglevel}"])


@cli.command()
def test():
    """Runs the unit tests without test coverage."""
    import pytest
    print(TEST_PATH)
    rv = pytest.main([TEST_PATH, "--verbose"])
    sys.exit(rv)


@cli.command()
def cov():
    """Runs the unit tests with coverage."""
    import pytest
    rv = pytest.main(["--verbose", "--cov=project project/tests", "--cov", "--cov-report=term"])
    sys.exit(rv)


@cli.command()
def flake():
    """Runs flake8 on the project."""
    subprocess.run(["flake8", "project"])


if __name__ == "__main__":
    cli()
