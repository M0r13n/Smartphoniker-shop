from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Iterable, Any

import requests as r

from project.server.common.escape import cleanify_dict

CUSTOMER_KEY_MAPPING = [
    ('tricoma_id', 'id'),
    ('registered_on', 'registered_on'),
    ('tricoma_username', 'username'),
    ('first_name', 'vorname'),
    ('last_name', 'name'),
    ('street', 'strasse'),
    ('zip_code', 'plz'),
    ('city', 'ort'),
    ('tel', 'telefon'),
    ('email', 'mail')
]


class TricomaFields(Enum):
    Salutation = 31
    Company = 46
    Referred_By = 78
    Handy = 63
    IBAN = 77
    Mail = 34
    Last_Name = 8
    First_Name = 9
    Location = 12
    Zip_Code = 11
    Street = 45
    Tel = 56
    Title = 33


CUSTOMER_DICT_MAPPING = dict(CUSTOMER_KEY_MAPPING)
TRICOMA_DICT_MAPPING = dict([(x[1], x[0]) for x in CUSTOMER_KEY_MAPPING])

CUSTOMER_TRICOMA_GROUP = ("110", "Price-Picker")

TRICOMA_DATE_FMT = "%Y-%m-%d - %H:%M:%S"


@dataclass
class TricomaCustomer(object):
    id: Any = ""
    registered_on: str = None
    username: str = ""
    vorname: str = ""
    name: str = ""
    strasse: str = ""
    plz: str = ""
    ort: str = ""
    mail: str = ""
    telefon: str = ""
    _kundengruppe: str = CUSTOMER_TRICOMA_GROUP[0]

    def to_list(self) -> list:
        return [(k, getattr(self, k)) for k in dir(self) if not callable(getattr(self, k)) and not k.startswith('_')]

    def to_db_model(self):
        from project.server.models import Customer
        c = Customer()
        for k in dir(self):
            if not callable(getattr(self, k)) and not k.startswith('_'):
                setattr(c, TRICOMA_DICT_MAPPING[k], getattr(self, k))
        return c

    @classmethod
    def from_db_model(cls, customer):
        c = cls()
        for customer_key, tricoma_key in CUSTOMER_KEY_MAPPING:
            setattr(c, tricoma_key, getattr(customer, customer_key))
        return c


def extract_customer_data(html_text) -> list:
    customers = []
    for c in filter(lambda y: len(y) == 4, [x.split('|') for x in html_text.splitlines()]):
        customer = TricomaCustomer(id=c[0], username=c[3])
        if len(c[1]) > 0:
            customer.registered_on = datetime.strptime(c[1], TRICOMA_DATE_FMT)

        customers.append(customer)
    return customers


class TricomaAPI(object):

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = None
        if base_url:
            self.init(base_url)

    def init_app(self, app):
        self.init(app.config.get('TRICOMA_API_URL'))

    def init(self, base_url):
        self.base_url = base_url

    @property
    def is_connected(self) -> bool:
        """
        Connected is True if base_url is not None
        """
        return self.base_url is not None

    def _assert_connected(self):
        if not self.is_connected:
            raise ValueError("This API is not properly set up. Please set the TRICOMA_API_URL in you environment!")

    def _get_request(self, params, cleanup_string=True) -> Optional[int]:
        """ Make a GET request and return customer id on success"""
        self._assert_connected()
        if cleanup_string:
            cleanify_dict(params)
        try:
            resp = r.get(self.base_url, params=params)
            customer_id = int(resp.text)
            return customer_id
        except ValueError:
            return None

    def test_connection(self) -> bool:
        """
        Test the connection to Tricoma.
        """
        try:
            resp = r.get(self.base_url)
            return resp.status_code == 200 and len(resp.text) > 0
        except Exception:
            return False

    def register_customer(self, customer: TricomaCustomer) -> Optional[int]:
        """
        Return customer id on success
        """
        _module = {'modul': 'kunden', 'modulkat': 'eintragen'}
        params = dict(customer.to_list())
        params.update(_module)
        return self._get_request(params=params)

    def fetch_customers(self) -> Optional[Iterable[TricomaCustomer]]:
        """
        Return a list of all customers that can be fetched via the API.
        """
        self._assert_connected()
        params = {'modul': 'kunden', 'modulkat': 'allekunden'}
        try:
            resp = r.get(self.base_url, params=params)
            # ID|Anlagedatum|gesperrt|Benutzername
            return extract_customer_data(resp.text)
        except ValueError:
            return None

    def update_field(self, customer_id, field_id: TricomaFields, value: str) -> Optional[int]:
        """
        It is possible to update a single data field.
        URL params are kundennummer, feldid, wert
        """
        params = {'modul': 'kunden', 'modulkat': 'aktualisieren', 'kundennummer': customer_id, 'feldid': field_id.value, 'wert': value}
        return self._get_request(params=params)
