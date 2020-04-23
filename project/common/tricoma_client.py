import functools
import sys
from typing import Iterable, Optional

import requests as r

from project.common.tricoma_api import TricomaCustomer


def extract_customers(raw_data: str) -> Optional[Iterable[TricomaCustomer]]:
    customers = []
    try:
        for customer in raw_data.splitlines()[1:]:
            customer = customer.split('|')
            customers.append(
                TricomaCustomer(
                    id=customer[0],
                    name=customer[2],
                    vorname=customer[3],
                    strasse=customer[5],
                    plz=customer[6],
                    ort=customer[7],
                    mail=customer[9],
                    telefon=customer[10]
                ))
    except IndexError as e:
        print(str(e), file=sys.stderr)
    return customers


def prepare_request(func):
    @functools.wraps(func)
    def check_auth(client, *args, **kwargs):
        if not client.authorised and not kwargs.get('ignore_auth', False):
            raise ValueError("Client not authorised")
        if 'ignore_auth' in kwargs:
            kwargs.pop('ignore_auth')

        return func(client, *args, **kwargs)

    return check_auth


class TricomaClient(object):

    def __init__(self, host: str = None, username: str = None, password: str = None, max_login_tries: int = 3):
        self.host = None
        self.base_url = None
        self.username = None
        self.password = None
        self.authorised = False
        self.session = None
        self.login_tries = 0
        self.max_login_tries = max_login_tries
        self.init(host, username, password)

    def init_app(self, app):
        self.init(app.config.get('TRICOMA_BASE_URL'), app.config.get('TRICOMA_USERNAME'), app.config.get('TRICOMA_PASSWORD'))

    def init(self, host: str, username: str, password: str):
        self.host = host
        self.base_url = f'https://{host}'
        self.username = username
        self.password = password
        self.login_tries = 0
        self.session = r.Session()
        headers = {
            'Host': host,
            'Origin': self.base_url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
        }
        self.session.headers.update(headers)
        if host and username and password:
            self.login(self.username, self.password)

    @prepare_request
    def post(self, url, data, allow_redirects=True, headers=None) -> Optional[r.Response]:
        return self.session.post(url, data=data, allow_redirects=allow_redirects, headers=headers, timeout=None)

    def login(self, username, password) -> Optional[r.Response]:
        if not username or not password:
            raise ValueError("Missing username or password")
        if self.login_tries >= self.max_login_tries:
            raise ValueError("Maximum Number of Login Tries exceeded! Please check you username and password")
        self.login_tries += 1
        url = self.base_url + "/cmssystem/index2_v2.php?hash=37da19249883c67f3ac2eb27c73b361eedf82b8a6029d8c56ed93b8a4b6"
        params = {
            'adminnick': username,
            'pw': password,
            'windowheight': 1200,
            'windowwidth': 1920,
            'sprache': 'deu',
            'submitbuton': ''
        }
        response = self.post(url, params, ignore_auth=True)
        self.authorised = response.status_code == 200
        return response

    def export_customers(self, kn=0) -> Optional[r.Response]:
        url = self.base_url + '/cmssystem/kunden/export_laden.php'
        headers = {
            'Sec-Fetch-Dest': 'iframe',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1'
        }

        params = {
            'nachrichtenkategorie': '',
            'kundennummer': kn,
            'exportauswahl': 'exports_standard_export_kunden',
            'modul': 'kunden',
            'submit_csv': ''
        }
        response = self.post(url, data=params, headers=headers)
        return response
