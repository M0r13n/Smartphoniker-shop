from project.server import db
from project.server.models.base import BaseModel
from project.server.models.image import ImageMixin


class Repair(BaseModel, ImageMixin):
    """ Repair """

    __tablename__ = 'repair'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    price = db.Column(db.DECIMAL(7, 2), default=0)

    # Relations
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=True)
    device = db.relationship("Device")

    orders = db.relationship("OrderRepairAssociation", back_populates="repair", cascade="all, delete-orphan")

    def __repr__(self):
        return f"{self.device.name} {self.name}"

    def _get_image_name_for_class(self):
        from project.server.models.image import Image, Default
        if self.device.is_tablet:
            img = Image.query.filter(Image.name == "default_tablet_other.svg").first()
        else:
            img = Image.query.filter(Image.name == "default_phone_other.svg").first()
        return img or Image.query.filter(Image.repair_default == Default.true).first()
