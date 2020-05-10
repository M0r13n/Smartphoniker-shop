from sqlalchemy import Index, desc, func, any_, bindparam, asc

from project.server import db
from project.server.models.crud import CRUDMixin

color_device_table = db.Table('color_device',
                              db.Column('color_id', db.Integer, db.ForeignKey('color.id')),
                              db.Column('device_id', db.Integer, db.ForeignKey('device.id'))
                              )


class Color(db.Model, CRUDMixin):
    __tablename__ = 'color'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    color_code = db.Column(db.String(20))

    devices = db.relationship(
        "Device",
        secondary=color_device_table,
        back_populates="colors")

    def __repr__(self):
        return f"<{self.name} : {self.color_code}>"


class Device(db.Model, CRUDMixin):
    __tablename__ = "device"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    # Relations
    series_id = db.Column(db.Integer, db.ForeignKey('device_series.id'), nullable=False)
    series = db.relationship("DeviceSeries")
    colors = db.relationship(
        "Color",
        secondary=color_device_table,
        back_populates="devices"
    )
    orders = db.relationship("Order", back_populates="device")
    repairs = db.relationship("Repair", back_populates="device")

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

    def __repr__(self):
        return f"<Device: {self.name}>"
