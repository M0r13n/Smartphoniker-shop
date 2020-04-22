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


class TricomaClient(object):

    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.base_url = f'https://{host}'
        self.username = username
        self.password = password
        self.authorised = False
        self.session = r.Session()
        headers = {
            'Host': host,
            'Origin': self.base_url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
        }
        self.session.headers.update(headers)
        self.login(self.username, self.password)

    def post(self, url, data, allow_redirects=True, headers=None) -> Optional[r.Response]:
        return self.session.post(url, data=data, allow_redirects=allow_redirects, headers=headers)

    def login(self, username, password) -> Optional[r.Response]:
        url = self.base_url + "/cmssystem/index2_v2.php?hash=37da19249883c67f3ac2eb27c73b361eedf82b8a6029d8c56ed93b8a4b6"
        params = {
            'adminnick': username,
            'pw': password,
            'windowheight': 1200,
            'windowwidth': 1920,
            'sprache': 'deu',
            'submitbuton': ''
        }
        response = self.post(url, params)
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
        response = self.post(url, params, headers=headers)
        return response
