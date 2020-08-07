from webtest import TestResponse, Form

from project.server.models import Customer
from project.server.models.misc import MiscInquiry
from project.server.shop.forms import MiscForm

REQUIRED_TEXT = "Dieses Feld wird benötigt"
MAIL_REQUIRED_TEXT = "Bitte gib eine gültige Email Adresse an"


class TestMisc:
    def test_form_requires_first_name(self, app):
        form = MiscForm()
        assert not form.validate()
        assert REQUIRED_TEXT in form.first_name.errors

    def test_form_requires_lat_name(self, app):
        form = MiscForm()
        assert not form.validate()
        assert REQUIRED_TEXT in form.last_name.errors

    def test_form_text(self, app):
        form = MiscForm(first_name="Leon", last_name="Morten")
        assert not form.validate()

        form.problem_description.data = "Text 123"
        assert not form.validate()
        assert "Die Beschreibung muss zwischen 30 und 5000 Zeichen lang sein" in form.problem_description.errors

        form.problem_description.data = "A" * 31
        assert not form.validate()
        assert not form.problem_description.errors

        form.email.data = "12"
        assert not form.validate()

        form.email.data = "hello@there.com"
        assert form.validate()

    def test_create_enquiry_non_existing_customer(self, app, db):
        form = MiscForm(
            first_name="leon",
            last_name="richter",
            email="leon@mail.com",
            problem_description="A" * 30
        )
        assert MiscInquiry.query.count() == 0
        enquiry: MiscInquiry = form.create_inquiry()
        assert enquiry
        assert isinstance(enquiry.customer, Customer)
        assert enquiry.customer.first_name == "leon"
        assert enquiry.customer.last_name == "richter"
        assert enquiry.description == "A" * 30
        assert MiscInquiry.query.count() == 1

    def test_create_enquiry_existing_customer(self, app, sample_customer: Customer):
        form = MiscForm(
            first_name=sample_customer.first_name,
            last_name=sample_customer.last_name,
            email=sample_customer.email,
            problem_description="A" * 100
        )
        enquiry: MiscInquiry = form.create_inquiry()
        assert enquiry
        assert isinstance(enquiry.customer, Customer)
        assert enquiry.customer == sample_customer
        assert enquiry.description == "A" * 100
        assert MiscInquiry.query.count() == 1

    def test_customer_submits_twice(self, app, sample_customer):
        form = MiscForm(
            first_name=sample_customer.first_name,
            last_name=sample_customer.last_name,
            email=sample_customer.email,
            problem_description="A" * 30
        )
        form.create_inquiry()
        form.create_inquiry()
        form.create_inquiry()
        assert MiscInquiry.query.count() == 3
        assert Customer.query.count() == 1

    def test_form_is_rendered(self, testapp):
        response: TestResponse = testapp.get("/anfrage")
        form: Form = response.form
        assert form
        assert form.fields['first_name']
        assert form.fields['last_name']
        assert form.fields['email']
        assert form.fields['problem_description']

    def test_form_post_correct_data(self, testapp, sample_customer):
        assert not MiscInquiry.query.count()
        payload = {
            'first_name': sample_customer.first_name,
            'last_name': sample_customer.last_name,
            'email': sample_customer.email,
            'problem_description': "ABC" * 123
        }
        response: TestResponse = testapp.post("/anfrage", params=payload)
        assert response.status_code == 302
        assert MiscInquiry.query.count() == 1

    def test_real_form_submit_missing_data(self, testapp, db):
        assert not MiscInquiry.query.count()
        payload = {
            'email': None,
            'problem_description': "ABC" * 123
        }
        response: TestResponse = testapp.post("/anfrage", params=payload)
        assert response.status_code == 200
        assert not MiscInquiry.query.count()
        assert MAIL_REQUIRED_TEXT in response
