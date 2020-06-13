# project/server/main/views.py
import typing

from flask import render_template, Blueprint, jsonify, abort, redirect, url_for, current_app, flash

from project.common.email.message import make_html_mail
from project.server.main.forms import SelectRepairForm, RegisterCustomerForm, FinalSubmitForm
from project.server.models import Manufacturer, DeviceSeries, Device, Customer, Order
from project.server.models.queries import get_bestsellers
from project.server.utils.mail import send_email
from project.tasks.tricoma import register_customer as tricoma_register

main_blueprint = Blueprint("main", __name__)


@main_blueprint.route("/")
def home():
    """ Render Homepage """
    bestseller: typing.List[Device] = get_bestsellers()
    specialist_manufacturers = Manufacturer.query.filter(
        (Manufacturer.name == "Apple") | (Manufacturer.name == "Samsung") | (Manufacturer.name == "Huawei")
    ).all()
    return render_template("main/home.html", bestseller=bestseller, specialist_manufacturers=specialist_manufacturers)


@main_blueprint.route("/manufacturer")
def manufacturer():
    """ Render a list of all manufacturers as a starting point """
    all_manufacturers: [Manufacturer] = Manufacturer.query.filter(Manufacturer.activated == True).all()  # noqa
    all_manufacturers_with_repairs = filter(lambda manu: len(manu.series) > 0, all_manufacturers)
    return render_template("main/manufacturer.html", manufacturers=all_manufacturers_with_repairs)


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
    _devices = list(filter(lambda device: len(device.repairs) > 0, _series.devices))  # display only devices that have at least one repair
    return render_template("main/devices.html", devices=_devices, manufacturer=manufacturer_name, series=series_name)


@main_blueprint.route("/<string:manufacturer_name>/<string:series_name>/<string:device_name>/", methods=['GET', 'POST'])
def model(manufacturer_name, series_name, device_name):
    """ Returns the chosen device """
    _manufacturer: Manufacturer = Manufacturer.query.filter(Manufacturer.name == manufacturer_name).first()
    _series: DeviceSeries = DeviceSeries.query.filter(DeviceSeries.name == series_name).first()
    _device: Device = Device.query.filter(Device.name == device_name).first()
    if not _manufacturer or not _series or not _device:
        abort(404)

    repair_form = SelectRepairForm(_device)
    if repair_form.validate_on_submit():
        order = Order.create(
            color=repair_form.get_color(),
            repairs=repair_form.get_repairs(),
            problem_description=repair_form.problem_description.data
        )
        order.save()
        order.save_to_session()
        return redirect(url_for('main.register_customer'))

    return render_template("main/modell.html", device=_device, repair_form=repair_form, manufacturer=manufacturer_name, series=series_name)


@main_blueprint.route("/register", methods=['GET', 'POST'])
def register_customer():
    """ Customer enters his/her personal data """
    customer_data_form = RegisterCustomerForm()
    if customer_data_form.validate_on_submit():
        customer = Customer()
        customer_data_form.populate_obj(customer)
        customer.save()
        customer.save_to_session()
        # also register customer in tricoma
        register_tricoma_if_enabled(customer)
        return redirect(url_for('main.order_overview'))

    return render_template("main/customer.html", customer_data_form=customer_data_form)


@main_blueprint.route("/order", methods=['GET', 'POST'])
def order_overview():
    """ A overview about customer data and the repair(s) """
    order: Order = Order.get_from_session()
    if not order or not len(order.repairs) > 0:
        flash("Es wurde noch keine Reparatur ausgewählt", "error")
        return redirect(url_for('main.home'))

    customer: Customer = Customer.get_from_session()
    if not customer:
        flash("Sie müssen sich erst registrieren", "warning")
        return redirect(url_for('main.register_customer'))

    order.customer = customer
    form = FinalSubmitForm()
    if form.validate_on_submit():
        form.populate_order(order)
        order.save()
        # send confirmation mail to customer and notify shop
        send_mails(form.kva_button.data, form.shipping_label.data)
        return redirect(url_for('main.success'))

    return render_template(
        "main/order.html",
        color=order.color,
        repairs=order.repairs,
        problem_description=order.problem_description,
        device=order.device,
        customer=customer,
        total_cost=order.total_cost,
        taxes=order.taxes,
        discount=order.discount,
        total_cost_including_tax_and_discount=f"{order.total_cost_including_tax_and_discount:.2f}",
        form=form
    )


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


def send_mails(kva: bool, shipping: bool):
    order_dto: Order = Order.get_from_session()
    customer: Customer = Customer.get_from_session()
    body = render_template(
        "mails/order.html",
        tricoma_id=customer.tricoma_id,
        first_name=customer.first_name,
        last_name=customer.last_name,
        email=customer.email,
        tel=customer.tel,
        street=customer.street,
        zip=customer.zip_code,
        city=customer.city,
        kva=kva,
        shop=order_dto.shop,
        device=order_dto.device,
        repairs=order_dto.repairs,
        discount=order_dto.discount,
        total_price=order_dto.total_cost_including_tax_and_discount,
        shipping_required=shipping,
        problem_description=order_dto.problem_description,
        color=order_dto.color
    )
    order = make_html_mail(to_list=current_app.config['NOTIFICATION_MAILS'], from_address=current_app.config['MAIL_DEFAULT_SENDER'],
                           subject="Neue Anfrage über den Pricepicker", html_body=body, text_body=body)

    send_email(order)
    confirmation = make_html_mail(to_list=[customer.email], from_address=current_app.config['MAIL_DEFAULT_SENDER'],
                                  subject="Ihre Anfrage bei Smartphoniker", html_body=render_template("mails/confirmation.html"))
    send_email(confirmation)


def register_tricoma_if_enabled(customer: Customer):
    """ Register the customer on tricoma if TRICOMA_API_URL and is set """
    conf = current_app.config
    if conf.get("TRICOMA_API_URL") and conf.get("REGISTER_CUSTOMER_IN_TRICOMA"):
        try:
            tricoma_register.apply_async(args=(customer.serialize(),))
        except Exception as e:
            current_app.logger.error(e)
