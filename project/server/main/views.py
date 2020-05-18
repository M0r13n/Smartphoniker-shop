# project/server/main/views.py
from flask import render_template, Blueprint, jsonify, abort

from project.common.email.message import make_html_mail
from project.server.main.forms import SelectRepairForm
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
    _manufacturer = Manufacturer.query.filter(Manufacturer.name == manufacturer_name).first()
    if not _manufacturer:
        abort(404)
    return render_template("main/series.html", series=_manufacturer.series, manufacturer=manufacturer_name)


@main_blueprint.route("/<string:manufacturer_name>/<string:series_name>")
def all_devices_of_series(manufacturer_name, series_name):
    """ Return all devices of a series, e.g. all iPhones """
    _manufacturer = Manufacturer.query.filter(Manufacturer.name == manufacturer_name).first()
    _series = DeviceSeries.query.filter(DeviceSeries.name == series_name).first()
    if not _manufacturer or not _series:
        abort(404)
    return render_template("main/devices.html", devices=_series.devices, manufacturer=manufacturer_name, series=series_name)


@main_blueprint.route("/<string:manufacturer_name>/<string:series_name>/<string:device_name>/", methods=['GET', 'POST'])
def model(manufacturer_name, series_name, device_name):
    """ Returns the chosen device """
    _manufacturer = Manufacturer.query.filter(Manufacturer.name == manufacturer_name).first()
    _series = DeviceSeries.query.filter(DeviceSeries.name == series_name).first()
    _device = Device.query.filter(Device.name == device_name).first()
    if not _manufacturer or not _series or not _device:
        abort(404)

    repair_form = SelectRepairForm(_device)
    if repair_form.validate_on_submit():
        print("SUCCESS", repair_form.color.data, repair_form.repairs.data, repair_form.problem_description.data)
    return render_template("main/modell.html", device=_device, repair_form=repair_form)


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
    found_devices = Device.query.all()

    return render_template('main/search.html', devices=found_devices)


@main_blueprint.route("/order")
def order():
    """ Render overview on customer data """
    return render_template('main/order.html')


@main_blueprint.route("/customer")
def customer():
    """ Render Form for Customer Contact Data """
    return render_template('main/customer.html')


@main_blueprint.route("/success")
def success():
    """ Render successful order page """
    return render_template('main/success.html')


@main_blueprint.route("/api/search/<string:device_name>/")
def search_api(device_name):
    """
    Test endpoint for development
    """
    found_devices_normal = Device.search(device_name).all()
    found_devices_similar = Device.search_order_by_similarity(device_name).all()
    found_devices_array = Device.search_by_array(device_name).all()
    found_devices_levenshtein = Device.search_levenshtein(device_name).all()
    return jsonify(results={
        'normal': [device.name for device in found_devices_normal],
        'similar': [device.name for device in found_devices_similar],
        'array': [device.name for device in found_devices_array],
        'levenshtein': [device.name for device in found_devices_levenshtein],
    })


@main_blueprint.route("/mail")
def send_mail():
    """ Test route """
    html_body = render_template("mails/example_mail.html", user="Tim")
    msg = make_html_mail(to_list=["leon.morten@gmail.com"], from_address="anfrage@smartphoniker.de",
                         subject="Ich will das hier html drinnen ist", html_body=html_body, text_body="Das ist text!!!!!!11111elf!!!!")
    send_email(msg)
    return jsonify(dict(status="Task received"))
