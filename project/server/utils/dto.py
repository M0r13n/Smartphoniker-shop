"""
Data-Transfer-Objects
"""
import typing
from functools import reduce

from project.server.models import Color, Repair
from project.server.utils.session_mixin import SessionStoreMixin


class CustomerRepair(SessionStoreMixin):
    """
    DTO for storing the submitted repair order in the current user's session
    """
    SESSION_KW = 'repair'

    def __init__(self, device_color: Color, repairs: typing.Iterable[Repair], problem_description: str):
        self.device_color: Color = device_color
        self.repairs: typing.FrozenSet[Repair] = frozenset(repairs)
        self.problem_description: str = problem_description
        self.ensure_same_device()

    def __repr__(self):
        return f"<CustomerRepair: {self.repairs}>"

    def __dict__(self) -> dict:
        return dict(
            device_color=self.device_color,
            repairs=self.repairs,
            problem_description=self.problem_description
        )

    def ensure_same_device(self):
        if len(set(map(lambda rep: rep.device, self.repairs))) > 1:
            raise ValueError("All repairs must belong to the same device!")

    @classmethod
    def deserialize(cls, obj):
        try:
            instance = cls(
                device_color=Color.query.get(obj['device_color']),
                repairs=list(map(lambda repair_id: Repair.query.get(repair_id), obj['repairs'])),
                problem_description=obj['problem_description']
            )
            return instance
        except KeyError as error:
            raise ValueError(f"{obj} is an invalid CustomerRepairDTO") from error

    def serialize(self) -> dict:
        return dict(
            device_color=self.device_color.id,
            repairs=list(map(lambda repair: repair.id, self.repairs)),
            problem_description=self.problem_description
        )

    @property
    def total_cost(self):
        tot = reduce(lambda total, cost: total + cost, map(lambda repair: repair.price, self.repairs))
        return round(tot, 2)

    @property
    def taxes(self):
        return round((19.0 * float(self.total_cost)) / 100.0, 2)

    @property
    def discount(self):
        """ Discount is 20 percentage on the cheapest repair"""
        if len(self.repairs) > 1:
            cheapest = min(self.repairs, key=lambda repair: repair.price)
            discount = round((20.0 * float(cheapest.price)) / 100.0, 2)
            return discount
        return 0

    @property
    def total_cost_including_tax_and_discount(self):
        return round(float(self.total_cost) - float(self.discount), 2)
