from sqlalchemy.exc import IntegrityError

from project.server.models import Order


class TestOrder:

    def test_create(self, db, sample_device, sample_color, sample_customer, sample_shop):
        # Require arguments
        try:
            order = Order.create()
            assert False
        except IntegrityError:
            db.session.rollback()

        # Require color
        try:
            order = Order.create(device=sample_device)
            assert False
        except IntegrityError:
            db.session.rollback()

        # Require customer
        try:
            order = Order.create(device=sample_device, color=sample_color)
            assert False
        except IntegrityError:
            db.session.rollback()

        # Require shop
        try:
            order = Order.create(device=sample_device, color=sample_color, customer=sample_customer)
            assert False
        except IntegrityError:
            db.session.rollback()

        order = Order.create(device=sample_device, color=sample_color, customer=sample_customer, shop=sample_shop)
        assert order
        assert not order.complete
        assert order.customer == sample_customer
        assert order.device == sample_device
        assert order.shop == sample_shop
        assert order.color == sample_color
