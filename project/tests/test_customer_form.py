from project.server.shop.forms import RegisterCustomerForm
from project.server.models import Customer


class TestCustomerForm:
    def test_lower_limits(self, app):
        """Login successful."""
        form = RegisterCustomerForm()

        form.first_name.data = ""
        form.last_name.data = ""
        form.street.data = ""
        form.zip_code.data = ""
        form.city.data = ""
        form.email.data = ""
        assert not form.validate()
        assert "Dieses Feld wird benötigt" in form.first_name.errors
        assert "Dieses Feld wird benötigt" in form.last_name.errors
        assert "Dieses Feld wird benötigt" in form.street.errors
        assert "Dieses Feld wird benötigt" in form.zip_code.errors
        assert "Dieses Feld wird benötigt" in form.city.errors
        assert "Dieses Feld wird benötigt" in form.email.errors

    def test_upper_limits(self, app):
        """Login successful."""
        form = RegisterCustomerForm()

        form.first_name.data = "A" * 256
        form.last_name.data = "A" * 256
        form.street.data = "A" * 256
        form.zip_code.data = "A" * 11
        form.city.data = "A" * 256
        form.tel.data = "A" * 66
        form.tricoma_id.data = "A" * 66
        assert not form.validate()
        assert "Der Name muss zwischen 1 und 255 Zeichen lang sein" in form.first_name.errors
        assert "Der Name muss zwischen 1 und 255 Zeichen lang sein" in form.last_name.errors
        assert "Die Straße muss zwischen 1 und 255 Zeichen lang sein" in form.street.errors
        assert "Die PLZ muss zwischen 3 und 10 Zeichen lang sein" in form.zip_code.errors
        assert "Die Stadt muss zwischen 1 und 255 Zeichen lang sein" in form.city.errors
        assert "Die Nummer muss zwischen 3 und 64 Zeichen lang sein" in form.tel.errors
        assert "Die Nummer muss zwischen 1 und 64 Zeichen lang sein" in form.tricoma_id.errors

    def test_populate_min(self, db, app):
        form = RegisterCustomerForm()
        form.first_name.data = "A"
        form.last_name.data = "A"
        form.street.data = "A"
        form.zip_code.data = "AAA"
        form.city.data = "A"
        form.tel.data = "AAA"
        form.tricoma_id.data = "A"
        form.email.data = "A@B.C"
        assert form.validate()
        customer = Customer()
        form.populate_obj(customer)
        customer.save()
        assert customer.first_name == form.first_name.data
        assert customer.last_name == form.last_name.data
        assert customer.street == form.street.data
        assert customer.zip_code == form.zip_code.data
        assert customer.city == form.city.data
        assert customer.tel == form.tel.data
        assert customer.email == form.email.data

    def test_populate_max(self, db, app):
        form = RegisterCustomerForm()
        form.first_name.data = "A" * 255
        form.last_name.data = "A" * 255
        form.street.data = "A" * 255
        form.zip_code.data = "A" * 10
        form.city.data = "A" * 64
        form.tel.data = "A" * 64
        form.tricoma_id.data = "A" * 64
        form.email.data = "A" * 60 + "@d.c"
        assert form.validate()
        customer = Customer()
        form.populate_obj(customer)
        customer.save()
        assert customer.first_name == form.first_name.data
        assert customer.last_name == form.last_name.data
        assert customer.street == form.street.data
        assert customer.zip_code == form.zip_code.data
        assert customer.city == form.city.data
        assert customer.tel == form.tel.data
        assert customer.email == form.email.data
