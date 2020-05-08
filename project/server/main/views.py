# project/server/main/views.py
from flask import render_template, Blueprint, jsonify, abort

from project.common.email.message import make_html_mail
from project.server.models import Repair, Manufacturer, DeviceSeries, Device
from project.server.utils import send_email

main_blueprint = Blueprint("main", __name__)


@main_blueprint.route("/")
def home():
    """ Render Homepage """
    bestseller = Repair.query.filter(Repair.bestseller == True).all()  # noqa
    return render_template("main/home.html", bestseller=bestseller)


@main_blueprint.route("/shop")
def shop():
    """ Render a list of all manufacturers """
    all_manufacturers = Manufacturer.query.filter(Manufacturer.activated == True).all()  # noqa
    return render_template("main/shop.html", manufacturers=all_manufacturers)


@main_blueprint.route("/manufacturer")
def manufacturer():
    """ Render a list of all manufacturers as a starting point """
    all_manufacturers = Manufacturer.query.filter(Manufacturer.activated == True).all()  # noqa
    return render_template("main/manufacturer.html", manufacturers=all_manufacturers)


@main_blueprint.route("/<string:manufacturer_name>/series")
def series(manufacturer_name):
    """ Return all series of the manufacturer, e.g. iPhone, iPad, etc """
    m = Manufacturer.query.filter(Manufacturer.name == manufacturer_name).first()
    if not m:
        abort(404)
    return render_template("main/series.html", series=m.series, manufacturer=manufacturer_name)


@main_blueprint.route("/<string:manufacturer_name>/<string:series_name>")
def all_devices_of_series(manufacturer_name, series_name):
    """ Return all devices of a series, e.g. all iPhones """
    m = Manufacturer.query.filter(Manufacturer.name == manufacturer_name).first()
    s = DeviceSeries.query.filter(DeviceSeries.name == series_name).first()
    if not m or not s:
        abort(404)
    return render_template("main/devices.html", devices=s.devices, manufacturer=manufacturer_name, series=series_name)


@main_blueprint.route("/<string:manufacturer_name>/<string:series_name>/<string:device_name>/")
def modell(manufacturer_name, series_name, device_name):
    """ Returns the chosen device """
    device_name = device_name.replace("%", " ")
    m = Manufacturer.query.filter(Manufacturer.name == manufacturer_name).first()
    s = DeviceSeries.query.filter(DeviceSeries.name == series_name).first()
    d = Device.query.filter(Device.name == device_name).first()
    if not m or not s or not d:
        abort(404)
    return render_template("main/modell.html", device=d, colors=d.colors, repairs=d.repairs)


@main_blueprint.route("/agb")
def agb():
    """ Render Terms and Services """
    return render_template('main/agb.html')


@main_blueprint.route("/datenschutz")
def datenschutz():
    """ Render Privacy """
    return render_template('main/datenschutz.html')


@main_blueprint.route("/faq")
def faq():
    """ Render FAQ """
    return render_template('main/faq.html')


@main_blueprint.route("/impressum")
def impressum():
    """ Render about """
    return render_template('main/impressum.html')


@main_blueprint.route("/search/<string:device_name>/")
def search(device_name):
    """ Render Search Results """
    tag = device_name.replace("$", "%")
    search = "%{}%".format(tag)
    if device_name == 'all':
        s = Device.query.all()
        tag = ''
    else:
        s = Device.query.filter(Device.name.ilike(search)).all()
        tag = tag.replace("%", " ")
    # TODO @ Leon man macht doch kein Like....
    return render_template('main/search.html', devices=s, search=tag)


@main_blueprint.route("/mail")
def send_mail():
    """ Test route """
    html_body = render_template("mails/example_mail.html", user="Tim")
    msg = make_html_mail(to_list=["leon.morten@gmail.com"], from_address="anfrage@smartphoniker.de",
                         subject="Ich will das hier html drinnen ist", html_body=html_body, text_body="Das ist text!!!!!!11111elf!!!!")
    send_email(msg)
    return jsonify(dict(status="Task received"))
