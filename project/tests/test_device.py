import random
import string

from project.server.models import Device


class TestDevice:

    def test_order(self, db, sample_series, sample_color):
        letters = string.ascii_lowercase
        devices = [
            Device.create(name=''.join(random.choice(letters) for x in range(10)), colors=[sample_color], series=sample_series) for i in range(10)
        ]
        assert len(devices) == 10
        for i, device in enumerate(devices):
            assert device.order_index == i

    def test_normalize(self, db, sample_series, sample_color):
        letters = string.ascii_lowercase
        devices = [
            Device.create(name=''.join(random.choice(letters) for x in range(10)), colors=[sample_color], series=sample_series) for i in range(10)
        ]
        for d in devices:
            d.order_index = 0
            d.save()

        Device.normalize()
        for i, device in enumerate(devices):
            assert device.order_index == i

    def test_move_up(self, db, sample_series, sample_color):
        letters = string.ascii_lowercase
        devices = [
            Device.create(name=''.join(random.choice(letters) for x in range(10)), colors=[sample_color], series=sample_series) for i in range(10)
        ]

        last = devices[-1]
        last_1 = devices[-2]
        assert last.order_index > last_1.order_index

        last.move_up()
        assert last.order_index < last_1.order_index

        for i in range(100):
            last.move_up()
        assert last.order_index == 0

    def test_move_down(self, db, sample_series, sample_color):
        letters = string.ascii_lowercase
        devices = [
            Device.create(name=''.join(random.choice(letters) for x in range(10)), colors=[sample_color], series=sample_series) for i in range(10)
        ]

        first = devices[0]
        first_1 = devices[1]
        assert first.order_index < first_1.order_index

        first.move_down()
        assert first.order_index > first_1.order_index

        for i in range(100):
            first.move_down()
        assert first.order_index == 9
