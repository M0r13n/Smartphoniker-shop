from project.server import db
from project.server.models.crud import CRUDMixin


class Manufacturer(db.Model, CRUDMixin):
    __tablename__ = "manufacturer"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)

    # Relations
    devices = db.relationship("Device", back_populates="manufacturer")

    def __repr__(self):
        return f"<Manufacturer: {self.name}>"
