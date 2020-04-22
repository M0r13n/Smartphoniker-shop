# manage.py
import os
import subprocess
import sys

import coverage
from flask.cli import FlaskGroup

from project.server.app import create_app, db
from project.server.models import User

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
    pass


@cli.command()
def create_db():
    """ Drops all existing tables and creates them afterwards """
    db.drop_all()
    db.create_all()
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
