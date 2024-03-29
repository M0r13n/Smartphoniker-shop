# project/server/shop/views.py

import typing

from flask import render_template, Blueprint, jsonify, abort, redirect, url_for, flash, session, request

from project.server.extensions import cache
from project.server.models import Manufacturer, DeviceSeries, Device, Customer, Order
from project.server.models.queries import get_bestsellers
from project.server.shop.actions import perform_post_complete_actions
from project.server.shop.forms import SelectRepairForm, RegisterCustomerForm, FinalSubmitForm, MiscForm
from project.tasks.email import notify_shop_about_inquiry
from project.tasks.tricoma import register_tricoma_if_enabled

main_blueprint = Blueprint("shop_blueprint", __name__)


@main_blueprint.route("/")
@main_blueprint.route("/home")
@cache.cached()
def home():
    """
    Render Homepage
    --------------------------------------------------------------
    This site should be cached, because it is the main entry point for many users.
    """
    bestseller: typing.List[Device] = get_bestsellers()
    specialist_manufacturers = Manufacturer.query.filter(
        (Manufacturer.name == "Samsung") | (Manufacturer.name == "Huawei")
    ).all()
    return render_template("shop/home.html", bestseller=bestseller, specialist_manufacturers=specialist_manufacturers)


@main_blueprint.route("/manufacturer")
@cache.cached()
def manufacturer():
    """
    Render a list of all manufacturers as a starting point
    --------------------------------------------------------------
    This site should be cached, because it is the main entry point for many users.
    """
    all_manufacturers: typing.List[Manufacturer] = Manufacturer.query.filter(Manufacturer.activated == True).all()  # noqa
    all_manufacturers_with_repairs = filter(lambda manu: len(manu.series) > 0, all_manufacturers)
    return render_template("shop/manufacturer.html", manufacturers=list(all_manufacturers_with_repairs), manufacturer_names=[manu.name for manu in all_manufacturers_with_repairs])


@main_blueprint.route("/<string:manufacturer_name>")
@main_blueprint.route("/<string:manufacturer_name>/series")
def series(manufacturer_name):
    """ Return all series of the manufacturer, e.g. iPhone, iPad, etc """
    _manufacturer = Manufacturer.query.filter(Manufacturer.name == manufacturer_name).first()
    if not _manufacturer:
        abort(404)
    return render_template("shop/series.html", series=_manufacturer.series, manufacturer=manufacturer_name, series_names=[s.name for s in _manufacturer.series])


@main_blueprint.route("/<string:manufacturer_name>/<string:series_name>")
def all_devices_of_series(manufacturer_name, series_name):
    """ Return all devices of a series, e.g. all iPhones """
    _manufacturer = Manufacturer.query.filter(Manufacturer.name == manufacturer_name).first()
    _series = DeviceSeries.query.filter(DeviceSeries.name == series_name).first()
    if not _manufacturer or not _series:
        abort(404)
    # order devices by order_index with name as a fallback
    _devices = Device.query.filter(Device.series_id == _series.id).order_by(Device.order_index.asc(), Device.name.desc())
    _devices = [device for device in _devices if len(device.repairs)]  # display only devices that have at least one repair
    return render_template("shop/devices.html", devices=_devices, manufacturer=manufacturer_name, series=series_name, device_names=[d.name for d in _devices])


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
            problem_description=repair_form.problem_description.data,
        )
        order.save()
        order.save_to_session()
        return redirect(url_for('.register_customer'))

    return render_template("shop/modell.html", device=_device, repair_form=repair_form, manufacturer=manufacturer_name, series=series_name, repair_names=[f"{rep.device.name} {rep.name}" for rep in _device.repairs])


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
        return redirect(url_for('.order_overview'))

    return render_template("shop/customer.html", customer_data_form=customer_data_form)


@main_blueprint.route("/order", methods=['GET', 'POST'])
def order_overview():
    """ A overview about customer data and the repair(s) """
    order: Order = Order.get_from_session()
    if not order or not len(order.repairs) > 0:
        flash("Es wurde noch keine Reparatur ausgewählt", "error")
        return redirect(url_for('.home'))

    customer: Customer = Customer.get_from_session()
    if not customer:
        flash("Sie müssen sich erst registrieren", "warning")
        return redirect(url_for('.register_customer'))

    order.customer = customer
    form = FinalSubmitForm()
    if form.validate_on_submit():
        # ORDER SUBMITTED
        form.populate_order(order)
        order.save()
        perform_post_complete_actions(order)
        return redirect(url_for('.success'))

    return render_template(
        "shop/order.html",
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
    return render_template('shop/agb.html')


@main_blueprint.route("/datenschutz")
def datenschutz():
    """ Render Privacy """
    return render_template('shop/datenschutz.html')


@main_blueprint.route("/faq")
def faq():
    """ Render FAQ """
    return render_template('shop/faq.html')


@main_blueprint.route("/impressum")
def impressum():
    """ Render about """
    return render_template('shop/impressum.html')


@main_blueprint.route("/search/<string:device_name>/")
def search(device_name):
    """ Render Search Results """
    found_devices = Device.query.all()
    return render_template('shop/search.html', devices=found_devices)


@main_blueprint.route("/success")
def success():
    """ Render successful order page """
    session.clear()
    return render_template('shop/success.html')


@main_blueprint.route("/referenzen")
def references():
    """ Render references page """
    return render_template('shop/references.html')


@main_blueprint.route("/anfrage", methods=['GET', 'POST'])
def other():
    """ Render other enquiry page """
    form = MiscForm()
    if form.validate_on_submit():
        inquiry = form.create_inquiry()
        notify_shop_about_inquiry(inquiry)
        flash("Danke. Wir haben Ihre Anfrage erhalten!", "success")
        return redirect(url_for(".home"))
    return render_template('shop/other.html', other_inquiry_form=form)


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


@main_blueprint.before_request
def check_affiliate():
    """ Check if the customer is a new customer who was redirected by an affiliate. """
    affiliate_track_id = request.args.get('t')
    if affiliate_track_id:
        session['affiliate_track_id'] = affiliate_track_id
