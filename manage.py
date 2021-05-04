#!/usr/bin/env python3
import csv
import logging
import os
import subprocess
import sys
from pathlib import Path

import click
import coverage
from flask.cli import FlaskGroup
from sqlalchemy.exc import IntegrityError, InvalidRequestError

from project.server.app import create_app, db
from project.server.models import *
from project.server.models.device import Color
from project.server.models.image import Default

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

    # Manus
    Manufacturer.create(name="ASUS")
    apple = Manufacturer.create(name="Apple", activated=True)
    Manufacturer.create(name="BlackBerry")
    Manufacturer.create(name="Blackview")
    Manufacturer.create(name="CAT")
    Manufacturer.create(name="Cubot")
    Manufacturer.create(name="Emporia")
    Manufacturer.create(name="Google")
    Manufacturer.create(name="Honor")
    Manufacturer.create(name="HTC", activated=True)
    Manufacturer.create(name="Huawei", activated=True)
    Manufacturer.create(name="LG")
    Manufacturer.create(name="Medion")
    Manufacturer.create(name="Motorola")
    Manufacturer.create(name="Nokia")
    Manufacturer.create(name="OnePlus")
    Manufacturer.create(name="Oppo")
    Manufacturer.create(name="Razer")
    Manufacturer.create(name="Samsung", activated=True)
    Manufacturer.create(name="Sony", activated=True)
    Manufacturer.create(name="Ulefone")
    Manufacturer.create(name="Vivo")
    Manufacturer.create(name="Wiko")
    Manufacturer.create(name="Xiaomi", activated=True)
    Manufacturer.create(name="ZTE")

    # load svgs
    load_images()
    load_color_csv()

    iphone = DeviceSeries.create(manufacturer=apple, name="iPhone")
    dev = Device.create(series=iphone, name="iPhone X", colors=[Color.query.first()])
    Repair.create(device=dev, name="Display")

    # Set default image for devices
    device_default_img_name = "default_phone.svg"
    img = Image.query.filter(Image.name == device_default_img_name).first()
    img.device_default = Default.true
    img.save()
    # Set default image for tablets
    tablet_default_img_name = "default_tablet.svg"
    img = Image.query.filter(Image.name == tablet_default_img_name).first()
    img.tablet_default = Default.true
    img.save()
    # Set default image for repair
    repair_default_img_name = "default_phone_kleinteil.svg"
    img = Image.query.filter(Image.name == repair_default_img_name).first()
    img.repair_default = Default.true
    img.save()


def load_images():
    img_path = "client/static/images"
    search_dir = os.path.join(PROJECT_ROOT, img_path)
    assert os.path.exists(search_dir)

    rootdir = Path(search_dir)
    counter = 0
    for f in rootdir.glob('**/*'):
        if f.is_file() and f.exists() and f.suffix == '.svg':
            f = f.relative_to(rootdir)
            file = f.parts[-1]
            if not Image.query.filter(Image.name == file).first():
                counter += 1
                i = Image.create(path=str(f.as_posix()), name=file)
                assert os.path.exists(os.path.join(search_dir, i.path))
    print("Loaded", counter, "images into db.")


def load_color_csv():
    path = "data/colorlist.csv"
    file = os.path.join(PROJECT_ROOT, path)
    assert os.path.exists(file)
    counter = 0
    with open(file, "r") as csv_file:
        colors = csv.reader(csv_file, delimiter=',')
        for color_name, color_code, internal_name in colors:
            try:
                Color.create(name=color_name, color_code=color_code, internal_name=internal_name)
                counter += 1
            except (IntegrityError, InvalidRequestError):
                print(internal_name, "already exists. Skipping.")
                db.session.rollback()
    print("Loaded", counter, "colors into db.")


@cli.command()
def load_color():
    """ Load color from CSV """
    load_color_csv()


@cli.command()
def create_db():
    """ Drops all existing tables and creates them afterwards """
    print("Dropping tables...")
    db.drop_all()
    print("Creating tables...")
    db.create_all()
    print("Committing...")
    db.session.commit()
    print("DB created successfully!")


@cli.command()
def drop_db():
    """Drops the db tables."""
    db.drop_all()


@cli.command()
def create_admin():
    """Creates the admin user."""
    User.create(email="ad@min.com", password="admin", admin=True)
    print("Created default admin user: 'ad@min.com':'admin'.")


@cli.command()
def create_data():
    """Creates sample data."""
    create_sample_data()
    print("Created sample data.")


@cli.command()
def load_svg():
    """ Load all SVG's from a default path """
    load_images()


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
    rv = pytest.main([TEST_PATH, "--verbose"])
    sys.exit(rv)


@cli.command()
def cov():
    """Runs the unit tests with coverage."""
    import pytest
    rv = pytest.main(["-x", "--verbose", "--cov=project project/tests", "--cov", "--cov-report=term"])
    sys.exit(rv)


@cli.command()
def flake():
    """Runs flake8 on the project."""
    subprocess.run(["flake8", "project"])


@cli.command()
def test_sentry():
    """ Raise an exception which should be displayed on sentry. Don't worry: This method always throws an exception :-P """
    logger = logging.getLogger(__name__)
    logger.error("I am a test log message")
    raise ValueError("This should be visible on sentry.io")


if __name__ == "__main__":
    cli()
