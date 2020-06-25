from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Iterable, Any

import requests as r

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
        self._assert_connected()
        _module = {'modul': 'kunden', 'modulkat': 'eintragen'}
        params = dict(customer.to_list())
        params.update(_module)
        try:
            resp = r.get(self.base_url, params=params)
            customer_id = int(resp.text)
            return customer_id
        except ValueError:
            return None

    def fetch_customers(self) -> Optional[Iterable[TricomaCustomer]]:
        self._assert_connected()
        params = {'modul': 'kunden', 'modulkat': 'allekunden'}
        try:
            resp = r.get(self.base_url, params=params)
            # ID|Anlagedatum|gesperrt|Benutzername
            return extract_customer_data(resp.text)
        except ValueError:
            return None
