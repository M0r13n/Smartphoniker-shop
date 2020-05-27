from project.server import db
from project.server.models.crud import CRUDMixin


class DeviceSeries(db.Model, CRUDMixin):
    """ Association table between Device and Manufacturer """
    __tablename__ = "device_series"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)

    # Relations
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('manufacturer.id'), nullable=False)
    manufacturer = db.relationship("Manufacturer")

    devices = db.relationship("Device", back_populates="series")

    def __repr__(self):
        return self.name
