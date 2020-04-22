import os

import pytest

from project.common.tricoma_api import TricomaCustomer, TricomaAPI, extract_customer_data, TRICOMA_DATE_FMT
from project.common.tricoma_client import TricomaClient, extract_customers
from project.server.models import Customer


class TestTricomaAPI:
    """ Tricoma API """

    def test_active(self):
        # create an inactive API
        api = TricomaAPI(base_url=None)
        assert not api.is_connected
        assert not api.test_connection()

        try:
            api.fetch_customers()
            assert 1 == 2
        except ValueError as e:
            assert "TRICOMA_API_URL" in str(e)

        try:
            api.register_customer(TricomaCustomer())
            assert 1 == 2
        except ValueError as e:
            assert "TRICOMA_API_URL" in str(e)

    def test_extraction(self, db):
        mock_response = """
26956|2019-05-13 - 19:15:01|0|Hello
26957|2019-05-13 - 19:25:11|0|Some
26958|2019-05-14 - 10:15:18|0|Customer
26959|2019-05-14 - 10:15:46|0|
26960|2019-05-14 - 10:23:06|0|xx@yy.dd
26961|2019-05-14 - 10:24:50|0|
"""
        customers = extract_customer_data(mock_response)
        for customer in customers:
            assert isinstance(customer, TricomaCustomer)

        customer = customers[0]
        assert customer.id == "26956"
        assert customer.registered_on.strftime(TRICOMA_DATE_FMT) == "2019-05-13 - 19:15:01"
        assert customer.username == "Hello"

        # Test bulk insert
        for customer in customers:
            db.session.add(customer.to_db_model())
        db.session.commit()

    def test_customer_transformation(self, db):
        c = TricomaCustomer(
            username="Test",
            id="12345",
            vorname="Some",
            name="Dude",
            mail="some@dude.com",
            telefon="+49 124 4566 456",
            strasse="Some street 34",
            plz="124",
            ort="City 12"
        )
        model = c.to_db_model()
        assert model.tricoma_username == "Test"
        assert model.tricoma_id == "12345"
        assert model.first_name == "Some"
        assert model.last_name == "Dude"
        assert model.email == "some@dude.com"
        assert model.tel == "+49 124 4566 456"
        assert model.street == "Some street 34"
        assert model.zip_code == "124"
        assert model.city == "City 12"

        db.session.add(model)
        db.session.commit()

    def test_model_transformation(self, db):
        c = Customer.create(
            tricoma_username="1",
            tricoma_id="2",
            first_name="3",
            last_name="4",
            email="5",
            tel="6",
            street="7",
            zip_code="8",
            city="9",
        )
        cc = TricomaCustomer.from_db_model(c)
        assert isinstance(cc, TricomaCustomer)

        assert cc.username == "1"
        assert cc.id == "2"
        assert cc.vorname == "3"
        assert cc.name == "4"
        assert cc.mail == "5"
        assert cc.telefon == "6"
        assert cc.strasse == "7"
        assert cc.plz == "8"
        assert cc.ort == "9"

    def test_with_real_api(self, db):
        url = os.getenv("TRICOMA_API_URL")
        if url is None:
            pytest.skip("Skipping Real World Tricoma API test, because TRICOMA_API_URL is not set.")
            return

        api = TricomaAPI(base_url=url)
        assert api.is_connected
        assert api.test_connection()

        customers = api.fetch_customers()
        assert isinstance(customers, list)
        assert isinstance(customers[0], TricomaCustomer)
        assert isinstance(customers[0].to_db_model(), Customer)
        assert customers[0].to_db_model().save()


class TestTricomaClient:
    def test_wrong_client(self):
        client = TricomaClient("example.com", "some", "user")
        assert client.host == "example.com"
        assert client.base_url == "https://example.com"
        assert client.username == "some"
        assert client.password == "user"
        assert not client.authorised
        assert client.export_customers().status_code == 404

    def test_extract_method(self):
        sample = "ID|Anrede|Nachname|Vorname|Firma|Strasse|PLZ|Ort|Land|Email|Telefon|Fax|Kategorie|\n" \
                 "33053|Frau|Sabine|Wurst|Firma ABC|Straße str. 47|12345|Kiel||foto@domain.com|123456|||"
        customer = extract_customers(sample)
        assert isinstance(customer, list)
        assert len(customer) == 1
        assert isinstance(customer[0], TricomaCustomer)
        c: TricomaCustomer = customer[0]
        assert c.id == "33053"
        assert c.name == "Sabine"
        assert c.vorname == "Wurst"
        assert c.strasse == "Straße str. 47"
        assert c.plz == "12345"
        assert c.ort == "Kiel"
        assert c.mail == "foto@domain.com"
        assert c.telefon == "123456"

    def test_client(self):
        url = os.getenv("TRICOMA_BASE_URL")
        username = os.getenv("TRICOMA_USERNAME")
        password = os.getenv("TRICOMA_PASSWORD")
        if url is None or username is None or password is None:
            pytest.skip("Skipping Real World Tricoma Client test, because TRICOMA LOGIN DATA is not set.")
            return
        client = TricomaClient(url, username, password)
        assert client.authorised

        response = client.export_customers(34207)
        test_user = extract_customers(response.text)[0]
        assert test_user
        # Don't worry. This is not a real customer. Its a test customer that I created for testing :-)
        assert test_user.id == "34207"
        assert test_user.name == "Richter"
        assert test_user.vorname == "Leon"
        assert test_user.mail == "Leon"
