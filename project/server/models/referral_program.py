"""
Models for the referral program
"""
import uuid
from datetime import datetime, date, timedelta

from flask import url_for
from flask_sqlalchemy import BaseQuery
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property

from project.server import db
from project.server.models import Order
from project.server.models.crud import CRUDMixin


class ReferralPartner(db.Model, CRUDMixin):
    __tablename__ = "referral_partner"

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String(64), unique=True, index=True, nullable=False)

    # Relations
    db.relationship("Order", back_populates="referral_partner")

    @hybrid_property
    def ref_link(self):
        return url_for('main.home', ref_id=self.id)

    @hybrid_property
    def referrals(self) -> BaseQuery:
        return Order.query.filter(
            Order.complete == True,  # noqa
            Order.referral_partner_id == self.id,
        )

    @hybrid_property
    def referral_count(self) -> int:
        return self.referrals.count()

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
        return self.referrals.filter(Order.timestamp.between(date(*start), date(*end)))

    def referral_count_between(self, start: datetime, end: datetime) -> int:
        return self.referrals_between(start, end).count()
