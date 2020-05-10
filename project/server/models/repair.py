from project.server import db
from project.server.models.crud import CRUDMixin
from project.server.models.image import ImageMixin


class Repair(db.Model, CRUDMixin, ImageMixin):
    """ Repair """

    __tablename__ = 'repair'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    price = db.Column(db.DECIMAL(7, 2), default=0)
    bestseller = db.Column(db.Boolean, default=False)

    # Relations
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    device = db.relationship("Device")

    def __repr__(self):
        return f"{self.device.name} {self.name}"
