"""
Models for the referral program
"""
import typing
import uuid
from datetime import datetime, date, timedelta

from flask import url_for
from flask_sqlalchemy import BaseQuery
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property

from project.server import db
from project.server.models.crud import CRUDMixin


class Referral(db.Model, CRUDMixin):
    __tablename__ = 'referral'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    billed_timestamp = db.Column(db.DateTime)

    @hybrid_property
    def billed(self):
        return bool(self.billed_timestamp)

    @billed.setter
    def billed(self, billed: bool):
        if billed and not self.billed_timestamp:
            self.billed_timestamp = datetime.now()
        if not billed and self.billed_timestamp:
            self.billed_timestamp = None

    # order - relation
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False, unique=True)
    order = db.relationship("Order", back_populates="referral")

    # referral - relation
    partner_id = db.Column(db.Integer, db.ForeignKey('referral_partner.id'), nullable=False)
    partner = db.relationship("ReferralPartner", back_populates="referrals")

    def __init__(self, *args, **kwargs):
        super(Referral, self).__init__(*args, **kwargs)
        assert self.order.complete


class ReferralPartner(db.Model, CRUDMixin):
    __tablename__ = "referral_partner"

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String(64), unique=True, index=True, nullable=False)

    # Relations
    referrals = db.relationship("Referral", back_populates="partner")

    @property
    def ref_link(self):
        return url_for('main.home', ref_id=self.uuid)

    @property
    def un_billed_referrals(self) -> typing.List[Referral]:
        return Referral.query.filter(
            Referral.partner_id == self.id,
            Referral.billed == False  # noqa
        ).all()

    @property
    def un_billed_referral_count(self) -> int:
        return len(self.un_billed_referrals)

    @property
    def total_referrals(self):
        return len(self.referrals)

    def bill(self) -> None:
        """ Set all referrals to billed as a bulk update """
        db.session.execute(Referral.__table__
                           .update()
                           .values(billed_timestamp=datetime.now())
                           .where(Referral.__table__.c.partner_id == self.id))

    def referrals_between(self, start: datetime, end: datetime) -> BaseQuery:
        """
        Get all referral orders that are between :start and :end
        --
        Both datetime objects are transformed to a single date.
        So start become the start day at 00:00:00 AM.
        And end date becomes end day at 00:59:59 PM
        """
        if not start or not end:
            raise ValueError("Start and end datetime objects required")
        start = (start.year, start.month, start.day)
        end += timedelta(days=1)
        end -= timedelta(seconds=1)
        end = (end.year, end.month, end.day)
        return Referral.query.filter(
            Referral.partner_id == self.id,
            Referral.timestamp.between(date(*start), date(*end))
        )
