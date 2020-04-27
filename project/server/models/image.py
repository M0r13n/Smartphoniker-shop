from flask import url_for
from sqlalchemy.ext.declarative.base import declared_attr
from sqlalchemy.orm import backref

from project.server import db
from project.server.models.crud import CRUDMixin


class ImageMixin(object):
    """ Mixin for creating a link to a SVG """

    @declared_attr
    def image_id(cls):
        return db.Column(db.Integer, db.ForeignKey('image.id', ondelete='SET NULL'))

    @declared_attr
    def image(cls):
        return db.relationship("Image")

    def get_image_path(self):
        if self.image:
            return self.image.get_path()


class Image(db.Model, CRUDMixin):
    """ Images and SVGS """

    __tablename__ = "image"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True)
    path = db.Column(db.String(1024), index=True)

    def __repr__(self):
        return f"<Image: {self.name}>"

    def get_path(self):
        return url_for('static', filename=f"images/{self.path}")
