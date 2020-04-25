# project/server/customer.py
import datetime

from project.server import db
from .crud import CRUDMixin


class Customer(CRUDMixin, db.Model):
    __tablename__ = "customer"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tricoma_id = db.Column(db.String, nullable=True, index=True)
    first_name = db.Column(db.String(255), nullable=False, unique=False, index=True)
    last_name = db.Column(db.String(255), nullable=False, unique=False, index=True)
    tricoma_username = db.Column(db.String(255), nullable=True, unique=False, index=False)
    street = db.Column(db.String(255), nullable=True, unique=False, index=True)
    zip_code = db.Column(db.String(10), nullable=True, unique=False, index=True)
    city = db.Column(db.String(255), nullable=True, unique=False, index=True)
    tel = db.Column(db.String(64), nullable=True, unique=False, index=True)
    email = db.Column(db.String(255), nullable=False, unique=False, index=True)
    registered_on = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    # Relations
    orders = db.relationship("Order", back_populates="customer")

    def __repr__(self):
        return f"<Customer {self.email}>"
