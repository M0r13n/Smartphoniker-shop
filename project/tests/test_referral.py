from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from project.server.common import is_referred_user, create_referral
from project.server.models import Order
from project.server.models.referral_program import ReferralPartner, Referral


class TestReferral:

    def test_uuid(self, db):
        partner = ReferralPartner.create(name="Computer Shop 123")
        assert partner.id
        assert isinstance(partner.uuid, UUID)

    def test_ref_url(self, db, app):
        partner = ReferralPartner.create(name="Computer Shop 123")
        assert partner.ref_link
        assert isinstance(partner.ref_link, str)
        assert '?ref_id=' + str(partner.uuid) in partner.ref_link

    def test_relation(self, db, sample_order, sample_partner: ReferralPartner):
        assert sample_partner.referrals == []
        sample_order.set_complete()
        ref = Referral.create(partner=sample_partner, order=sample_order)
        assert sample_partner.referrals == [ref]
        assert ref.order == sample_order

    def test_relation_multiple(self, db, sample_partner: ReferralPartner, sample_color):
        n = 10
        for i in range(n):
            order = Order.create(color=sample_color, complete=True)
            Referral.create(partner=sample_partner, order=order)

        assert len(sample_partner.referrals) == n

    def test_order_id_unique(self, sample_order, sample_partner):
        sample_order.set_complete()
        Referral.create(partner=sample_partner, order=sample_order)
        try:
            Referral.create(partner=sample_partner, order=sample_order)
            assert False
        except IntegrityError:
            return True

    def test_billed(self, db, sample_order, sample_partner: ReferralPartner, sample_color):
        sample_order.set_complete()
        ref = Referral.create(partner=sample_partner, order=sample_order)
        assert not ref.billed
        assert not ref.billed_timestamp
        ref.billed = True
        assert ref.billed
        assert ref.billed_timestamp

        n = 10
        for i in range(n):
            order = Order.create(color=sample_color, complete=True)
            Referral.create(partner=sample_partner, order=order)

        sample_partner.bill()
        for ref in Referral.query.all():
            assert ref.billed

    def test_referral_time_filter(self, db, sample_partner, sample_order):
        sample_order.set_complete()
        ref = Referral.create(partner=sample_partner, order=sample_order)

        # completed orders are included
        assert sample_partner.referrals_between(datetime.now() - timedelta(days=24), datetime.now()).all() == [ref]
        assert sample_partner.referrals_between(datetime.now() - timedelta(days=24), datetime.now() - timedelta(days=1)).all() == []

    def test_is_referred_user(self, db, app, sample_partner, testapp):
        url = '/?ref_id=' + str(sample_partner.uuid)
        response = testapp.get(url)
        assert is_referred_user(request_args=response.request.params)

    def test_is_not_referred_user(self, db, app, sample_partner, testapp):
        url = '/'
        response = testapp.get(url)
        assert not is_referred_user(request_args=response.request.params)

    def test_is_ref_user_args(self):
        assert is_referred_user(dict(ref_id=123))
        assert is_referred_user(dict(test=12, ref_id=123))
        assert not is_referred_user(dict(test=12))

    def test_create_referral_method(self, db, app, sample_partner, sample_order, testapp):
        sample_order.set_complete()
        assert create_referral("1243", sample_order) is None
        assert create_referral(None, sample_order) is None
        assert create_referral(sample_partner.uuid, sample_order) is not None
        assert len(sample_partner.referrals) == 1
