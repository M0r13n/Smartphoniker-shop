from flask import session

from project.server.models import Repair
from project.server.utils.dto import CustomerRepair


class TestRepairDTO:

    def test_deserialize(self, db, sample_color, sample_repair):
        another_repair = Repair.create(name="dfgdfgdfgdfg", price=69, device=sample_repair.device)
        dto = CustomerRepair(
            sample_color,
            [sample_repair, another_repair],
            "Some Text"
        )

        assert dto.device_color == sample_color
        assert dto.repairs == {sample_repair, another_repair}
        assert dto.problem_description == "Some Text"

        serialized = dto.serialize()
        a = serialized == {
            'device_color': sample_color.id,
            'repairs': [another_repair.id, sample_repair.id],
            'problem_description': "Some Text"
        }
        b = serialized == {
            'device_color': sample_color.id,
            'repairs': [sample_repair.id, another_repair.id],
            'problem_description': "Some Text"
        }
        assert a or b

        deserialized = CustomerRepair.deserialize(serialized)
        assert dto.repairs == deserialized.repairs
        assert dto.device_color == deserialized.device_color
        assert dto.problem_description == deserialized.problem_description

    def test_same_device(self, db, sample_color, sample_repair, another_repair):
        """ Assert that repairs can only have the same device """
        try:
            CustomerRepair(
                sample_color,
                [sample_repair, another_repair],
                "Some Text"
            )
            assert False
        except ValueError:
            return True

    def test_cost(self, db, sample_color, sample_repair):
        another_repair = Repair.create(name="dfgdfgdfgdfg", price=49, device=sample_repair.device)
        dto = CustomerRepair(
            sample_color,
            [sample_repair, another_repair],
            "Some Text"
        )

        assert dto.total_cost_including_tax_and_discount == 108.2
        assert dto.total_cost == 118
        assert dto.taxes == 22.42
        assert dto.discount == 9.8

    def test_session_save(self, db, sample_color, sample_repair):
        dto = CustomerRepair(
            sample_color,
            [sample_repair],
            "Some Text"
        )
        dto.save_to_session()
        assert session[CustomerRepair.get_session_kw()] == dto.serialize()
        assert CustomerRepair.get_from_session().device_color == dto.device_color
        assert CustomerRepair.get_from_session().repairs == dto.repairs
        assert CustomerRepair.get_from_session().problem_description == "Some Text"
