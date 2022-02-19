from project.server import db
from project.server.models import Device
from project.server.models.base import BaseModel
from project.server.models.image import ImageMixin


class Repair(BaseModel, ImageMixin):
    """ Repair """

    __tablename__ = 'repair'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    price = db.Column(db.DECIMAL(7, 2), default=0)

    # Make the device orderable
    order_index = db.Column(db.Integer, default=0, index=True)

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

    @classmethod
    def normalize(cls):
        """ Normalize all order indexes"""

        devices = Device.query.all()

        for device in devices:
            repairs = cls.query.filter(Repair.device_id == device.id).order_by(cls.order_index).all()
            for idx, item in enumerate(repairs):
                item.order_index = idx

        db.session.commit()

    def move_up(self):
        if self.order_index == 0:
            return

        # Get all repairs for the same device ordered by their index
        repairs = Repair.query.filter(Repair.device_id == self.device_id).order_by(Repair.order_index).all()
        idx = repairs.index(self)

        # swap with repair above
        above = repairs[idx - 1]
        above.order_index, self.order_index = idx, above.order_index
        db.session.commit()

    def move_down(self):
        # get all repairs ordered by their index
        items = Repair.query.filter(Repair.device_id == self.device_id).order_by(Repair.order_index).all()
        idx = items.index(self)

        # if item is last do nothing
        if idx == len(items) - 1:
            return

        # swap with item below
        below = items[idx + 1]
        below.order_index, self.order_index = idx, below.order_index
        db.session.commit()
