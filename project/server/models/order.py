import datetime
import typing
from functools import reduce

from project.server import db
from project.server.models.crud import CRUDMixin
from project.server.utils.session_mixin import SessionStoreMixin


class OrderRepairAssociation(db.Model, CRUDMixin):
    __tablename__ = 'order_repair_association'
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), primary_key=True)
    repair_id = db.Column(db.Integer, db.ForeignKey('repair.id'), primary_key=True)

    order = db.relationship("Order", back_populates="_repairs")
    repair = db.relationship("Repair", back_populates="orders")


class Order(db.Model, CRUDMixin, SessionStoreMixin):
    __tablename__ = "order"
    SESSION_KW = __tablename__

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    # Data
    complete = db.Column(db.Boolean, default=False, nullable=False)
    kva = db.Column(db.Boolean, default=False, nullable=False)
    customer_wishes_shipping_label = db.Column(db.Boolean, default=False)
    problem_description = db.Column(db.Text(), nullable=True)

    # Relations
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)
    customer = db.relationship("Customer", back_populates="orders")

    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=True)
    shop = db.relationship("Shop", back_populates="orders")

    color_id = db.Column(db.Integer, db.ForeignKey('color.id'), nullable=False)
    color = db.relationship("Color")

    # Set to NULL on delete
    referral_partner_id = db.Column(db.Integer, db.ForeignKey('referral_partner.id', ondelete='SET NULL'), nullable=True)
    referral_partner = db.relationship("ReferralPartner")

    # Repairs
    _repairs = db.relationship("OrderRepairAssociation", back_populates="order")

    def __repr__(self):
        return f"<Order: {self.device.name}>"

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.id == other.id

    def append_repair(self, repair) -> OrderRepairAssociation:
        ora = OrderRepairAssociation.create(
            order=self,
            repair=repair
        )
        return ora

    def append_repairs(self, repairs: typing.Iterable) -> typing.Iterable[OrderRepairAssociation]:
        oras = [self.append_repair(repair) for repair in repairs]
        return oras

    @classmethod
    def deserialize(cls, obj):
        try:
            order_id = obj['order_id']
            instance = cls.query.get(order_id)
            return instance
        except KeyError as error:
            raise ValueError(f"{obj} is an invalid OrderDTO") from error

    def serialize(self) -> dict:
        return dict(
            order_id=self.id
        )

    @property
    def total_cost(self) -> float:
        tot = reduce(lambda total, cost: total + cost, map(lambda repair: repair.price, self.repairs))
        return round(tot, 2)

    @property
    def taxes(self) -> float:
        return round((19.0 * float(self.total_cost_including_tax_and_discount)) / 100.0, 2)

    @property
    def discount(self) -> float:
        """ Discount is 20 percentage on the cheapest repair"""
        if len(self.repairs) > 1:
            cheapest = min(self.repairs, key=lambda repair: repair.price)
            discount = round((20.0 * float(cheapest.price)) / 100.0, 2)
            return discount
        return 0

    @property
    def total_cost_including_tax_and_discount(self) -> float:
        return round(float(self.total_cost) - float(self.discount), 2)

    @property
    def device(self) -> typing.Optional:
        if self.repairs and len(self.repairs) > 0:
            return self.repairs[0].device
        return None

    @property
    def repairs(self) -> typing.List:
        return self.get_repairs()

    @repairs.setter
    def repairs(self, repairs) -> None:
        try:
            self.append_repairs(repairs)
        except TypeError:
            self.append_repair(repair=repairs)

    def get_repairs(self) -> typing.List:
        return [ora.repair for ora in self._repairs]

    def set_complete(self) -> None:
        self.complete = True
        self.save()
