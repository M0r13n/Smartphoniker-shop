import typing

from sqlalchemy import Index, desc, func, any_, bindparam, asc

from project.server import db
from project.server.models.crud import CRUDMixin
from project.server.models.image import ImageMixin
from project.server.models.orderable import OrderableMixin

color_device_table = db.Table('color_device',
                              db.Column('color_id', db.Integer, db.ForeignKey('color.id')),
                              db.Column('device_id', db.Integer, db.ForeignKey('device.id'))
                              )


class Color(db.Model, CRUDMixin):
    __tablename__ = 'color'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)  # public name that is displayed to user's
    internal_name = db.Column(db.String(128), index=True, unique=True, nullable=False)  # internal name that we use to map colors to manufacturers
    color_code = db.Column(db.String(20), nullable=False)
    devices = db.relationship(
        "Device",
        secondary=color_device_table,
        back_populates="colors")

    def __repr__(self):
        return self.internal_name


class Device(db.Model, CRUDMixin, ImageMixin, OrderableMixin):
    __tablename__ = "device"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    is_tablet = db.Column(db.Boolean(), default=False)

    # Relations
    series_id = db.Column(db.Integer, db.ForeignKey('device_series.id'), nullable=False)
    series = db.relationship("DeviceSeries")

    colors = db.relationship(
        "Color",
        secondary=color_device_table,
        back_populates="devices"
    )

    repairs = db.relationship("Repair", back_populates="device", cascade="all, delete-orphan")

    __table_args__ = (
        Index(
            'name_idx', "name",
            postgresql_ops={"name": "gin_trgm_ops"},
            postgresql_using='gin'),
    )

    @classmethod
    def search(cls, q: str):
        """
        This method fuzzy searches the Device.name column.
        ----------
        SELECT * FROM devices WHERE name % 'SEARCH_KW';
        ----------
        """
        query = cls.query.filter(Device.name.op('%%')(q))
        return query

    @classmethod
    def search_order_by_similarity(cls, q: str):
        """
        SELECT * FROM devices WHERE name % 'SEARCH_KW' ORDER BY SIMILARITY(name, 'IPHONE 11') DESC;
        """
        query = cls.search(q)
        query = query.order_by(desc(func.similarity(cls.name, q)))
        return query

    @classmethod
    def search_by_array(cls, q: str):
        """
        SELECT * FROM devices WHERE 'X' % ANY(STRING_TO_ARRAY(name, ' '));
        """
        query = cls.query.filter(
            bindparam('string', q).op('%%')(any_(func.string_to_array(Device.name, ' ')))
        )
        return query

    @classmethod
    def search_levenshtein(cls, q: str, limit: int = 15):
        """
        SELECT * from devices order by LEVENSHTEIN(name, '11') ASC;
        """
        query = cls.query.order_by(asc(func.levenshtein(Device.name, q))).limit(limit)
        return query

    @classmethod
    def merge(cls, ids: typing.List[int]):
        """ Merge a list of devices (id's) into a one. Heavily opinionated method."""
        query = cls.query.filter(cls.id.in_(ids))
        with cls.session():
            # Copy basic data from the first device
            merger = _create_from_first_device(query[0])
            # Get the first non none image
            merger.image = next(filter(lambda i: i is not None, map(lambda d: d.image, query.all())), None)
            for device in query:
                # merge relations
                _merge_colors(merger, device.colors)
                _merge_repairs(merger, device.repairs)
                # dont forget to delete
                device.delete()
            merger.name = merger.name[:-1]
            return merger

    @property
    def manufacturer(self):
        return self.series.manufacturer

    def __repr__(self):
        return self.name or "n.a"

    def _get_image_name_for_class(self):
        from project.server.models.image import Image, Default
        if self.is_tablet:
            return Image.query.filter(Image.tablet_default == Default.true).first()  # noqa
        return Image.query.filter(Image.device_default == Default.true).first()  # noqa


def _create_from_first_device(first: Device) -> Device:
    name, is_tablet, series = first.name, first.is_tablet, first.series
    merger = Device.create(name=name + "#", is_tablet=is_tablet, series=series)
    return merger


def _merge_colors(merger: Device, colors: typing.List) -> None:
    for color in colors:
        if color not in merger.colors:
            merger.colors.append(color)


def _merge_repairs(merger: Device, repairs: typing.List) -> None:
    for repair in repairs:
        if repair.name not in map(lambda d: d.name, merger.repairs):
            rep = repair.clone()
            rep.device = merger
            rep.save()
            repair.delete()
