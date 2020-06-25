from project.server.main.forms import MiscForm
from project.server.models import Customer
from project.server.models.misc import MiscInquiry


class TestMisc:

    def test_form(self, db, app):
        form = MiscForm()
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

    def test_create_obj(self, db, app):
        form = MiscForm(
            email="leon@mail.com",
            problem_description="A" * 30
        )
        assert MiscInquiry.query.count() == 0
        enquiry: MiscInquiry = form.create_model()
        assert enquiry
        assert isinstance(enquiry.customer, Customer)
        assert enquiry.description == "A" * 30
        assert MiscInquiry.query.count() == 1

    def test_customer_submits_twice(self, db, app):
        form = MiscForm(
            email="leon@mail.com",
            problem_description="A" * 30
        )
        form.create_model()
        form.create_model()
        form.create_model()
        assert MiscInquiry.query.count() == 3
        assert Customer.query.count() == 1
