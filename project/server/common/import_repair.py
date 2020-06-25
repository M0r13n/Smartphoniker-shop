import csv
import decimal
import logging
import typing
from io import StringIO

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError

from project.server import db
from project.server.models import Manufacturer, DeviceSeries, Device, Color, Repair

logger = logging.getLogger(__name__)


def import_repairs(repair_file_content: str) -> typing.Tuple[int, str]:
    string = StringIO(repair_file_content)
    csv_reader = csv.reader(string, delimiter=',')
    headers = next(csv_reader)

    if not len(headers) == 6:
        return False, "Es werden genau 6 Spalten benötigt. Herstelle,Serie,Gerät,Farbe,Reparatur,Preis (in €)"

    counter = 0
    for manufacturer, series, device, color_string, repair, price_str in csv_reader:
        try:
            manufacturer = manufacturer_create_or_get(manufacturer)
            series = series_create_or_get(manufacturer, series)
            device = device_create_or_get(series, device)
            color = get_color(color_string)
            price = str_to_dec(price_str)

            if not color and color_string:
                return False, f"Farbe {color} existiert nicht im System. Bitte wähle eine existierende! Achte darauf, dass der internal_name als Name erwartet wird."

            if price is None:
                return False, f"Der Preis '{price_str}' scheint kein valider Preis zu sein."

            repair = create_new_or_skip_existing(repair, device, price)
            if repair:
                counter += 1
        except (IntegrityError, FlushError,) as e:
            logger.error(e)
            print(e)
            db.session.rollback()
            continue
    if counter == 0:
        return 0, "Keine neuen Reparturen gefunden"
    return counter, ""


def str_to_dec(price: str) -> typing.Optional[decimal.Decimal]:
    try:
        return decimal.Decimal(price.strip(' "'))
    except Exception:
        return None


def create_new_or_skip_existing(rep_name: str, device: Device, price: decimal.Decimal) -> typing.Optional[Repair]:
    repair = list(filter(lambda rep: rep.name == rep_name, device.repairs))
    if not repair:
        return Repair.create(name=rep_name, device=device, price=price)
    logger.debug(f"Skipping {repair} because it exists.")
    return None


def manufacturer_create_or_get(manufacturer: str) -> Manufacturer:
    manu = Manufacturer.query.filter(Manufacturer.name == manufacturer).first()
    if not manu:
        manu = Manufacturer.create(name=manufacturer, activated=True)

    return manu


def series_create_or_get(manufacturer: Manufacturer, series_name: str) -> DeviceSeries:
    series = DeviceSeries.query.filter(DeviceSeries.name == series_name).first()
    if not series:
        series = DeviceSeries.create(manufacturer=manufacturer, name=series_name)
    return series


def device_create_or_get(series: DeviceSeries, device_name: str) -> Device:
    device = Device.query.filter(Device.name == device_name).first()
    if not device:
        device = Device.create(series=series, name=device_name)
    return device


def get_color(color: str) -> typing.Optional[Color]:
    return Color.query.filter(Color.internal_name == color).first()
