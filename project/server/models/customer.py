# project/server/customer.py
import datetime
import typing

from project.server import db
from project.server.models.session_mixin import SessionStoreMixin
from .crud import CRUDMixin


class Customer(CRUDMixin, db.Model, SessionStoreMixin):
    __tablename__ = "customer"
    SESSION_KW = __tablename__

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tricoma_id = db.Column(db.String, nullable=True, index=True)
    first_name = db.Column(db.String(255), nullable=True, unique=False, index=True)
    last_name = db.Column(db.String(255), nullable=True, unique=False, index=True)
    tricoma_username = db.Column(db.String(255), nullable=True, unique=False, index=False)
    street = db.Column(db.String(255), nullable=True, unique=False, index=True)
    zip_code = db.Column(db.String(10), nullable=True, unique=False, index=True)
    city = db.Column(db.String(255), nullable=True, unique=False, index=True)
    tel = db.Column(db.String(64), nullable=True, unique=False, index=True)
    email = db.Column(db.String(255), nullable=False, unique=False, index=True)
    registered_on = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    # Relations
    orders = db.relationship("Order", back_populates="customer")
    enquiries = db.relationship("MiscInquiry", back_populates="customer")

    def __repr__(self):
        return self.first_name + " " + self.last_name

    @classmethod
    def deserialize(cls, obj):
        try:
            customer_id = obj['customer_id']
            instance = cls.query.get(customer_id)
            return instance
        except KeyError as error:
            raise ValueError(f"{obj} is an invalid CustomerRepairDTO") from error

    @classmethod
    def query_by_mail(cls, email: str) -> typing.Optional:
        return cls.query.filter(cls.email == email).first()

    def serialize(self) -> dict:
        return dict(
            customer_id=self.id
        )
