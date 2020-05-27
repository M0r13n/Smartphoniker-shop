import enum
import typing

from flask import url_for
from sqlalchemy.ext.declarative.base import declared_attr

from project.server import db
from project.server.models.crud import CRUDMixin


class Default(enum.Enum):
    """ A simple enum to make it possible to have a column that can only be True once """
    true = True


class Image(db.Model, CRUDMixin):
    """ Images and SVGS """

    __tablename__ = "image"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True, nullable=False)
    path = db.Column(db.String(1024), index=True, nullable=False)

    # There are four defaults: One for Devices, one for repairs, one for tablets and one for manufacturers
    # Use a enum instead of a Boolean and leave False fields None to make sure that only one img can be default
    device_default = db.Column(db.Enum(Default), unique=True)
    repair_default = db.Column(db.Enum(Default), unique=True)
    tablet_default = db.Column(db.Enum(Default), unique=True)
    manufacturer_default = db.Column(db.Enum(Default), unique=True)

    def __repr__(self):
        return self.name

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

    def _get_image_name_for_class(self):
        raise NotImplementedError()

    def get_image_path(self, default_fallback: bool = True) -> typing.Optional[str]:
        image = self.get_image(default_fallback=default_fallback)
        if image:
            return image.get_path()
        return None

    def get_image(self, default_fallback: bool = True) -> typing.Optional[Image]:
        if self.image:
            return self.image
        if default_fallback:
            return self._get_image_name_for_class()
