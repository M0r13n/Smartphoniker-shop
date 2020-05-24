#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

import click
import coverage
from flask.cli import FlaskGroup
from flask_alchemydumps.cli import alchemydumps

from project.server.app import create_app, db
from project.server.models import User, Shop, Customer, Manufacturer, Repair, Image, DeviceSeries
from project.server.models.device import Color, Device
from project.server.models.image import Default

app = create_app()
cli = FlaskGroup(create_app=create_app)

# Sub groups
cli.add_command(alchemydumps)

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
    a = Manufacturer.create(name="Apple", activated=True)
    s = DeviceSeries.create(name="iPhone", manufacturer=a)
    a1 = Device.create(name="iPhone 6S", colors=[b, w], series=s)
    a2 = Device.create(name="iPhone 7", colors=[b, w], series=s)
    Device.create(name="iPhone 6S Plus", colors=[b, w], series=s)
    Device.create(name="iPhone 6S +", colors=[b, w], series=s)
    Device.create(name="iPhone 9", colors=[b, w], series=s)
    Device.create(name="iPhone SE", colors=[b, w], series=s)
    Device.create(name="iPhone XS Max", colors=[b, w], series=s)
    Device.create(name="iPhone XS", colors=[b, w], series=s)
    Device.create(name="iPhone X", colors=[b, w], series=s)
    Device.create(name="iPhone 11", colors=[b, w], series=s)
    Device.create(name="iPhone Pro", colors=[b, w], series=s)

    Repair.create(name="Display Reparatur", device=a1, price=69)
    Repair.create(name="Akku Reparatur", device=a1, price=69)
    Repair.create(name="Kleinteilreparatur", device=a1, price=69)
    Repair.create(name="Display Reparatur", device=a2, price=69)

    # Some tablets
    tablet = DeviceSeries.create(name="iPad", manufacturer=a)
    ip11 = Device.create(name="iPad Pro 11\"", colors=[b], series=tablet, is_tablet=True)
    ip12 = Device.create(name="iPad Pro 12.9\"", colors=[b], series=tablet, is_tablet=True)

    Repair.create(name="Display Reparatur", device=ip11, price=169)
    Repair.create(name="Display Reparatur", device=ip12, price=69)
    Repair.create(name="Akku Reparatur", device=ip11, price=169)
    Repair.create(name="Akku Reparatur", device=ip12, price=69)

    # Manus
    Manufacturer.create(name="ASUS")
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

    User.create(email="ad@min.com", password="admin", admin=True)

    # load svgs
    load_images()

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
    rv = pytest.main(["--verbose", "--cov=project project/tests", "--cov", "--cov-report=term"])
    sys.exit(rv)


@cli.command()
def flake():
    """Runs flake8 on the project."""
    subprocess.run(["flake8", "project"])


if __name__ == "__main__":
    cli()
