from datetime import datetime, timedelta
from uuid import UUID

from project.server.models import Order, Color
from project.server.models.referral_program import ReferralPartner


class TestReferral:

    def test_uuid(self, db):
        partner = ReferralPartner.create(name="Computer Shop 123")
        assert partner.id
        assert isinstance(partner.uuid, UUID)

    def test_ref_url(self, db, app):
        partner = ReferralPartner.create(name="Computer Shop 123")
        assert partner.ref_link
        assert isinstance(partner.ref_link, str)
        assert '?ref_id=' + str(partner.id) in partner.ref_link

    def test_relation(self, db, sample_repair):
        sample_color = Color.create(name="Black", color_code="#000000", internal_name="TEEESSTPPP")
        assert sample_color
        order = Order.create(
            color=sample_color,
            repairs=[sample_repair],
        )
        order.save()
        assert order.referral_partner is None
        assert order.referral_partner_id is None

        partner = ReferralPartner.create(name="Computer Shop 123")
        order.referral_partner_id = str(partner.id)
        order.save()

        assert order.referral_partner is partner
        assert order.referral_partner_id is partner.id

    def test_referral_is_count_on_order(self, db, sample_repair):
        sample_color = Color.create(name="Black", color_code="#000000", internal_name="TEEESSTPPP")
        partner = ReferralPartner.create(name="Computer Shop 123")
        order = Order.create(
            color=sample_color,
            repairs=[sample_repair],
            referral_partner=partner
        )
        order.save()

        # uncompleted orders are omitted
        assert not order.complete
        assert partner.referrals.all() == []
        assert partner.referral_count == 0
        assert partner.referral_count_between(datetime.now() - timedelta(days=24), datetime.now()) == 0
        assert partner.referrals_between(datetime.now() - timedelta(days=24), datetime.now()).all() == []

        # completed orders are included
        order.set_complete()
        assert partner.referrals.all() == [order]
        assert partner.referral_count == 1
        assert partner.referral_count_between(datetime.now() - timedelta(days=24), datetime.now()) == 1
        assert partner.referrals_between(datetime.now() - timedelta(days=24), datetime.now()).all() == [order]
        assert partner.referrals_between(datetime.now() - timedelta(days=24), datetime.now() - timedelta(days=1)).all() == []

    def test_referral_between(self, db, sample_repair):
        # daterange works
        sample_color = Color.create(name="Black", color_code="#000000", internal_name="TEEESSTPPP")
        partner = ReferralPartner.create(name="Computer Shop 123")
        old_time_1 = datetime.now() - timedelta(days=31)
        order_1 = Order.create(
            color=sample_color,
            complete=True,
            timestamp=old_time_1,
            repairs=[sample_repair],
            referral_partner=partner,
        )

        old_time_2 = datetime.now() - timedelta(days=14)
        order_2 = Order.create(
            color=sample_color,
            complete=True,
            timestamp=old_time_2,
            repairs=[sample_repair],
            referral_partner=partner,
        )

        old_time_3 = datetime.now()
        order_3 = Order.create(
            color=sample_color,
            complete=True,
            timestamp=old_time_3,
            repairs=[sample_repair],
            referral_partner=partner,
        )

        # past orders
        assert partner.referral_count_between(datetime.now() - timedelta(days=13), datetime.now()) == 1
        assert partner.referral_count_between(datetime.now() - timedelta(days=14), datetime.now()) == 2
        assert partner.referral_count_between(datetime.now() - timedelta(days=24), datetime.now()) == 2
        assert partner.referral_count_between(datetime.now() - timedelta(days=32), datetime.now()) == 3
        assert partner.referral_count_between(datetime.now() - timedelta(days=365), datetime.now()) == 3

        assert partner.referral_count_between(datetime.now() - timedelta(days=13), datetime.now() - timedelta(1)) == 0
        assert partner.referral_count_between(datetime.now() - timedelta(days=14), datetime.now() - timedelta(1)) == 1
        assert partner.referral_count_between(datetime.now() - timedelta(days=24), datetime.now() - timedelta(1)) == 1
        assert partner.referral_count_between(datetime.now() - timedelta(days=32), datetime.now() - timedelta(1)) == 2
        assert partner.referral_count_between(datetime.now() - timedelta(days=365), datetime.now() - timedelta(1)) == 2

        assert partner.referral_count_between(datetime.now() - timedelta(days=365), datetime.now() - timedelta(days=32)) == 0

    def test_not_twice(self, db, sample_repair):
        sample_color = Color.create(name="Black", color_code="#000000", internal_name="TEEESSTPPP")
        partner = ReferralPartner.create(name="Computer Shop 123")
        saturday = datetime(year=2020, month=1, day=1, hour=23, minute=59, second=59)
        order_1 = Order.create(
            color=sample_color,
            complete=True,
            timestamp=saturday,
            repairs=[sample_repair],
            referral_partner=partner,
        )

        sunday = datetime(year=2020, month=1, day=2, hour=0, minute=9, second=1)
        order_1 = Order.create(
            color=sample_color,
            complete=True,
            timestamp=sunday,
            repairs=[sample_repair],
            referral_partner=partner,
        )
        monday = datetime(year=2020, month=1, day=3, hour=0, minute=9, second=1)
        assert partner.referral_count_between(saturday, sunday) == 2
        assert partner.referral_count_between(sunday, sunday) == 1
        assert partner.referral_count_between(monday, sunday) == 0
        assert partner.referral_count_between(sunday + timedelta(hours=3), sunday) == 1

    def test_referral_partner_deletes_set_null(self, db, sample_repair):
        sample_color = Color.create(name="Black", color_code="#000000", internal_name="TEEESSTPPP")
        partner = ReferralPartner.create(name="Computer Shop 123")
        saturday = datetime(year=2020, month=1, day=1, hour=23, minute=59, second=59)
        order_1 = Order.create(
            color=sample_color,
            complete=True,
            timestamp=saturday,
            repairs=[sample_repair],
            referral_partner=partner,
        )

        assert Order.query.all() == [order_1]
        assert ReferralPartner.query.all() == [partner]
        assert order_1.referral_partner is partner

        partner.delete()

        assert Order.query.all() == [order_1]
        assert ReferralPartner.query.all() == []

        assert Order.query.first() == order_1
        assert order_1.referral_partner is None
