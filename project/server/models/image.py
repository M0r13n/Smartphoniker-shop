import enum
import typing

from flask import url_for
from sqlalchemy.ext.declarative.base import declared_attr

from project.server import db
from project.server.models.crud import CRUDMixin


class Default(enum.Enum):
    true = True


class Image(db.Model, CRUDMixin):
    """ Images and SVGS """

    __tablename__ = "image"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True, nullable=False)
    path = db.Column(db.String(1024), index=True, nullable=False)

    # There are three defaults: One for Devices, one for repairs and one for manufacturers
    device_default = db.Column(db.Enum(Default), unique=True)
    repair_default = db.Column(db.Enum(Default), unique=True)
    manufacturer_default = db.Column(db.Enum(Default), unique=True)

    def __repr__(self):
        return f"<Image: {self.name}>"

    def get_path(self) -> str:
        return url_for('static', filename=f"images/{self.path}")


class ImageMixin(object):
    """ Mixin for creating a link to a SVG """

    @declared_attr
    def image_id(cls):
        return db.Column(db.Integer, db.ForeignKey('image.id', ondelete='SET NULL'))

    @declared_attr
    def image(cls):
        return db.relationship("Image")

    @staticmethod
    def _get_image_name_for_class(table):
        from project.server.models import Manufacturer, Repair, Device
        if table == Manufacturer.__tablename__:
            return Image.query.filter(Image.manufacturer_default == Default.true).first()  # noqa
        elif table == Repair.__tablename__:
            return Image.query.filter(Image.repair_default == Default.true).first()  # noqa
        elif table == Device.__tablename__:
            return Image.query.filter(Image.device_default == Default.true).first()  # noqa
        else:
            raise ValueError(f"Invalid tablename {table} for default image")

    def get_image_path(self, default_fallback: bool = True) -> typing.Optional[str]:
        image = self.get_image(default_fallback=default_fallback)
        if image:
            return image.get_path()
        return None

    def get_image(self, default_fallback: bool = True) -> typing.Optional[Image]:
        if self.image:
            return self.image
        if default_fallback:
            return self._get_image_name_for_class(self.__tablename__)
