import logging

from flask import current_app, session
from raider_reporter.reporter import RequestFailedError

from project.server.extensions import raider
from project.server.models import Order

logger = logging.getLogger("raider")


def track_payment(track_id: str, bonus: float, trace: str = None) -> bool:
    if track_id:
        try:
            return raider.track_payment(track_id, bonus, trace=trace)
        except RequestFailedError as e:
            logger.error(e)
        return False


def perform_post_complete_actions(order: Order) -> bool:
    order.notify()
    if not order.kva:
        return track_payment(session.get('affiliate_track_id'), current_app.config.get('AFFILIATE_BONUS'), trace=f"Order: {order.id}")
    return True
