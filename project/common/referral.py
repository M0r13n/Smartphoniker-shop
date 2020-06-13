import logging
import typing

from flask import session
from sqlalchemy.exc import DataError

from project.server import db
from project.server.models import Order, Referral, ReferralPartner

REF_ID_KW = 'ref_id'

logger = logging.getLogger(__name__)


def is_referred_user(request_args: dict):
    return request_args.get(REF_ID_KW, None) is not None


def save_referral_to_session(ref_id: str):
    session[REF_ID_KW] = ref_id


def get_referral_from_session():
    return session.get(REF_ID_KW, None)


def create_referral(ref_id: str, order: Order) -> typing.Optional[Referral]:
    if not ref_id:
        return None

    try:
        partner = ReferralPartner.query.filter(ReferralPartner.uuid == ref_id).first()
    except DataError:
        # this means that the string was not a valid UUID
        partner = None
        db.session.rollback()

    if not partner:
        logger.error(f"{ref_id} is not a valid Referral ID")
        return None
    return Referral.create(partner=partner, order=order)
