from project.server import db
from project.server.models.crud import CRUDMixin

color_device_table = db.Table('color_device',
                              db.Column('color_id', db.Integer, db.ForeignKey('color.id')),
                              db.Column('device_id', db.Integer, db.ForeignKey('device.id'))
                              )


class Color(db.Model, CRUDMixin):
    __tablename__ = 'color'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    color_code = db.Column(db.String(20))

    devices = db.relationship(
        "Device",
        secondary=color_device_table,
        back_populates="colors")

    def __repr__(self):
        return f"<{self.name} : {self.color_code}>"


class Device(db.Model, CRUDMixin):
    __tablename__ = "device"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)

    # Relations
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('manufacturer.id'), nullable=False)
    manufacturer = db.relationship("Manufacturer")

    colors = db.relationship(
        "Color",
        secondary=color_device_table,
        back_populates="devices"
    )

    orders = db.relationship("Order", back_populates="device")

    repairs = db.relationship("Repair", back_populates="device")

    def __repr__(self):
        return f"<Device: {self.name}>"
