import datetime

from project.server import db
from project.server.models.crud import CRUDMixin


class Order(db.Model, CRUDMixin):
    __tablename__ = "order"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    # Data
    complete = db.Column(db.Boolean, default=False)

    # Relations
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    customer = db.relationship("Customer", back_populates="orders")

    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    shop = db.relationship("Shop", back_populates="orders")

    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    device = db.relationship("Device", back_populates="orders")

    color_id = db.Column(db.Integer, db.ForeignKey('color.id'), nullable=False)
    color = db.relationship("Color")

    def __repr__(self):
        return f"<Order: {self.device.name}>"
