import typing

from flask import session
from sqlalchemy.exc import DataError

from project.server import db
from project.server.models import Order, Referral, ReferralPartner

REF_ID_KW = 'ref_id'


def is_referred_user(request_args: dict):
    return request_args.get(REF_ID_KW, None) is not None


def save_referral_to_session(ref_id: str):
    session[REF_ID_KW] = ref_id


def get_referral_from_session():
    return session.get(REF_ID_KW, None)


def create_referral(ref_id: str, order: Order) -> typing.Optional[Referral]:
    try:
        partner = ReferralPartner.query.filter(ReferralPartner.uuid == ref_id).first()
    except DataError as error:
        # this means that the string was not a valid UUID
        db.session.rollback()
        raise ValueError(f"{ref_id} is not a valid Referral ID") from error

    if not partner:
        raise ValueError(f"Partner #{ref_id} not found!")

    return Referral.create(partner=partner, order=order)


def create_referral_if_applicable(order):
    current_ref_id = get_referral_from_session()
    if current_ref_id:
        create_referral(current_ref_id, order)
