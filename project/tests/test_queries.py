from project.server.models import Order
from project.server.models.queries import most_selling_repairs, get_bestsellers


class TestQueries:

    def test_most_selling(self, sample_repair, sample_color, another_repair):
        assert most_selling_repairs() == []
        Order.create(color=sample_color, repairs=[sample_repair])
        assert most_selling_repairs() == [sample_repair]
        Order.create(color=sample_color, repairs=[another_repair])
        Order.create(color=sample_color, repairs=[another_repair])
        assert most_selling_repairs() == [another_repair, sample_repair]

    def test_get_bestsellers(self, sample_repair, another_repair, sample_color):
        assert get_bestsellers() == []
        Order.create(color=sample_color, repairs=[sample_repair])
        assert get_bestsellers() == [sample_repair.device]
        Order.create(color=sample_color, repairs=[another_repair])
        Order.create(color=sample_color, repairs=[another_repair])
        assert get_bestsellers() == [another_repair.device, sample_repair.device]
