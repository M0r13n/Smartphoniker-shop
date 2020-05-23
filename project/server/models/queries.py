"""
This is the place for complex queries
"""
import typing

from sqlalchemy import func, desc

from project.server import db
from project.server.models import OrderRepairAssociation, Repair, Device


def most_selling_repairs(limit: int = 5) -> typing.List[Repair]:
    repair_qty_tuples = db.session \
        .query(OrderRepairAssociation.repair_id, func.count(OrderRepairAssociation.repair_id).label('qty')) \
        .group_by(OrderRepairAssociation.repair_id) \
        .order_by(desc('qty')) \
        .limit(limit) \
        .all()
    return [Repair.query.get(rep_id) for (rep_id, _) in repair_qty_tuples]


def get_bestsellers(limit: int = 5) -> typing.List[Device]:
    repairs = most_selling_repairs(limit=limit)
    return list(set(map(lambda rep: rep.device, repairs)))
