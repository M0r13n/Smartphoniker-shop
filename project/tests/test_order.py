from flask import session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError

from project.server.models import Repair, Order


class TestOrder:

    def test_customer_not_required(self, db, sample_color, sample_shop):
        order = Order.create(color=sample_color, shop=sample_shop)
        assert order.customer is None

    def test_customer_relation(self, db, sample_color, sample_customer, sample_shop):
        order = Order.create(
            color=sample_color,
            shop=sample_shop,
            customer=sample_customer
        )
        assert order.customer == sample_customer

    def test_color_required(self, db):
        try:
            Order.create()
            assert False
        except IntegrityError:
            return True

    def test_set_repair(self, db, sample_color, sample_shop, sample_repair):
        order = Order.create(color=sample_color, shop=sample_shop)
        order.repairs = sample_repair
        assert len(order.repairs) == 1
        assert order.repairs == [sample_repair]
        assert order.repairs == order.get_repairs()

    def test_set_repairs(self, db, sample_color, sample_shop, sample_repair, another_repair):
        order = Order.create(color=sample_color, shop=sample_shop)
        order.repairs = [sample_repair, another_repair]
        assert len(order.repairs) == 2
        assert order.repairs == [sample_repair, another_repair]
        assert order.repairs == order.get_repairs()

    def test_add_repairs(self, db, sample_color, sample_shop, sample_repair, another_repair):
        order = Order.create(color=sample_color, shop=sample_shop)
        order.repairs = sample_repair
        order.append_repair(another_repair)
        assert len(order.repairs) == 2
        assert order.repairs == [sample_repair, another_repair]
        assert order.repairs == order.get_repairs()

    def remove_repair(self, db, sample_color, sample_shop, sample_repair, another_repair):
        order = Order.create(color=sample_color, shop=sample_shop)
        order.repairs = [sample_repair, another_repair]
        order.repairs -= [another_repair]
        assert len(order.repairs) == 1
        assert order.repairs == [sample_repair]
        assert order.repairs == order.get_repairs()

    def test_repair_cant_occur_twice(self, db, sample_color, sample_shop, sample_repair):
        order = Order.create(color=sample_color, shop=sample_shop)
        try:
            order.repairs = [sample_repair, sample_repair]
            assert False
        except FlushError:
            return True

    def test_deserialize(self, db, sample_color, sample_repair, sample_shop):
        another_repair = Repair.create(name="dfgdfgdfgdfg", price=69, device=sample_repair.device)
        dto = Order.create(
            color=sample_color,
            shop=sample_shop,
            problem_description="Some Text"
        )
        dto.append_repairs(repairs=[sample_repair, another_repair])

        assert dto.color == sample_color
        assert dto.repairs == [sample_repair, another_repair]
        assert dto.problem_description == "Some Text"

        serialized = dto.serialize()
        assert serialized == {
            'order_id': dto.id,
        }

        deserialized = Order.deserialize(serialized)
        assert dto == deserialized

    def test_cost(self, db, sample_color, sample_repair, sample_shop):
        another_repair = Repair.create(name="dfgdfgdfgdfg", price=49, device=sample_repair.device)
        dto = Order.create(
            color=sample_color,
            shop=sample_shop,
            repairs=[sample_repair, another_repair],
            problem_description="Some Text"
        )

        assert dto.total_cost_including_tax_and_discount == 108.2
        assert dto.total_cost == 118
        assert dto.taxes == 20.56
        assert dto.discount == 9.8

    def test_session_save(self, db, sample_color, sample_repair):
        order = Order.create(
            color=sample_color,
            repairs=sample_repair,
            problem_description="Some Text"
        )
        order.save_to_session()
        assert Order.SESSION_KW in session.keys()

    def test_session_save_overwrites(self, db, sample_color, sample_repair):
        order1 = Order.create(
            color=sample_color,
            repairs=sample_repair,
            problem_description="ABBBCCC"
        )
        order2 = Order.create(
            color=sample_color,
            repairs=sample_repair,
            problem_description="ABBBCCC"
        )
        order1.save_to_session()
        order2.save_to_session()
        assert Order.SESSION_KW in session.keys()
        assert Order.get_from_session() == order2
        assert Order.get_from_session() != order1

    def test_get_device(self, db, sample_color, sample_repair):
        order1 = Order.create(
            color=sample_color,
            repairs=sample_repair,
            problem_description="ABBBCCC"
        )
        assert order1.device == sample_repair.device

    def test_delete(self, db, sample_repair, sample_color):
        order1 = Order.create(
            color=sample_color,
            repairs=sample_repair,
            problem_description="123"
        )
        assert len(sample_repair.orders) == 1

        order1.delete()
        assert len(sample_repair.orders) == 0
