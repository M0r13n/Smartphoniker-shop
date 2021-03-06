from project.server import db
from project.server.models.base import BaseModel


class Shop(BaseModel):
    """ Shops """
    __tablename__ = 'shop'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), unique=True)

    # Relations
    orders = db.relationship("Order", back_populates="shop")

    def __repr__(self):
        return self.name
