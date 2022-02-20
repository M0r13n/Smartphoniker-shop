import random
import string

from sqlalchemy import asc

from project.server.models import Device, Repair


class TestDevice:

    def test_order(self, sample_series, sample_color):
        letters = string.ascii_lowercase
        devices = [
            Device.create(name=''.join(random.choice(letters) for x in range(10)), colors=[sample_color],
                          series=sample_series) for i in range(10)
        ]
        assert len(devices) == 10
        for i, device in enumerate(devices):
            assert device.order_index == i

    def test_normalize(self, sample_series, sample_color):
        letters = string.ascii_lowercase
        devices = [
            Device.create(name=''.join(random.choice(letters) for x in range(10)), colors=[sample_color],
                          series=sample_series) for i in range(10)
        ]
        for d in devices:
            d.order_index = 0
            d.save()

        Device.normalize()
        for i, device in enumerate(devices):
            assert device.order_index == i

    def test_move_up(self, sample_series, sample_color):
        letters = string.ascii_lowercase
        devices = [
            Device.create(name=''.join(random.choice(letters) for x in range(10)), colors=[sample_color],
                          series=sample_series) for i in range(10)
        ]

        last = devices[-1]
        last_1 = devices[-2]
        assert last.order_index > last_1.order_index

        last.move_up()
        assert last.order_index < last_1.order_index

        for i in range(100):
            last.move_up()
        assert last.order_index == 0

    def test_move_down(self, sample_series, sample_color):
        letters = string.ascii_lowercase
        devices = [
            Device.create(name=''.join(random.choice(letters) for x in range(10)), colors=[sample_color],
                          series=sample_series) for i in range(10)
        ]

        first = devices[0]
        first_1 = devices[1]
        assert first.order_index < first_1.order_index

        first.move_down()
        assert first.order_index > first_1.order_index

        for i in range(100):
            first.move_down()
        assert first.order_index == 9


class TestRepairSorting:
    def test_normalize(self, some_devices):
        for device in some_devices:
            # Create a display repair, a back-cover and a battery change
            Repair.create(device=device, name="Display")
            Repair.create(device=device, name="Back-cover")
            Repair.create(device=device, name="Battery")

        # Make sure all repairs were actually created
        assert Repair.query.count() == len(some_devices) * 3
        assert all([r.order_index == 0 for r in Repair.query.all()])

        Repair.normalize()

        repairs = Repair.query.all()
        # Normalize repairs should sort the repairs for every device
        # There should only be order indices from 0 to 2
        for rep in repairs:
            assert rep.order_index < 3
            assert rep.order_index >= 0

        # There should be an even amount of 0,1 and 2
        occurrences = {
            0: 0,
            1: 0,
            2: 0
        }
        for rep in repairs:
            occurrences[rep.order_index] += 1

        assert occurrences[0] == len(some_devices)
        assert occurrences[1] == len(some_devices)
        assert occurrences[2] == len(some_devices)

        # For every device there should be a repair with the idx of 0 and 1 and 2
        for dev in some_devices:
            reps = Repair.query.filter(Repair.device_id == dev.id).order_by(asc(Repair.order_index))
            assert reps[0].order_index == 0
            assert reps[1].order_index == 1
            assert reps[2].order_index == 2

    def test_query_order_by(self, sample_device):
        # Create a display repair, a back-cover and a battery change
        Repair.create(device=sample_device, name="Display")
        Repair.create(device=sample_device, name="Back-cover")
        Repair.create(device=sample_device, name="Battery")

        Repair.normalize()

        reps = sample_device.repairs
        assert reps[0].order_index == 0
        assert reps[1].order_index == 1
        assert reps[2].order_index == 2

    def test_move_up(self, some_devices):
        for device in some_devices:
            # Create a display repair, a back-cover and a battery change
            Repair.create(device=device, name="Display")
            Repair.create(device=device, name="Back-cover")
            Repair.create(device=device, name="Battery")

        for i, rep in enumerate(some_devices[0].repairs):
            rep.order_index = i

        rep.save()

        # If I move the last repair one up, it should be swapped with the above
        original = some_devices[0].repairs
        some_devices[0].repairs[-1].move_up()
        now = some_devices[0].repairs

        assert original[0] == now[0]
        assert original[1] == now[2]
        assert original[2] == now[1]

        # If I move it one more up, it should be swapped with the elem above
        some_devices[0].repairs[1].move_up()
        now = some_devices[0].repairs

        assert original[0] == now[1]
        assert original[1] == now[2]
        assert original[2] == now[0]

        # But if I move it up again nothing should happen
        some_devices[0].repairs[0].move_up()
        some_devices[0].repairs[0].move_up()
        some_devices[0].repairs[0].move_up()
        some_devices[0].repairs[0].move_up()

        assert some_devices[0].repairs[0].order_index == 0

        # All other repairs should remain unchanged
        assert all(rep.order_index == 0 for rep in Repair.query.all() if rep.device != some_devices[0])

    def test_move_down(self, some_devices):
        for device in some_devices:
            # Create a display repair, a back-cover and a battery change
            Repair.create(device=device, name="Display")
            Repair.create(device=device, name="Back-cover")
            Repair.create(device=device, name="Battery")

        for i, rep in enumerate(some_devices[0].repairs):
            rep.order_index = i

        rep.save()

        device = some_devices[0]

        # If I move the last repair one down, it should be swapped with the below
        original = device.repairs
        device.repairs[0].move_down()
        now = device.repairs

        assert original[0] == now[1]
        assert original[1] == now[0]
        assert original[2] == now[2]

        # If I move it one more down, it should be swapped with the elem below
        device.repairs[1].move_down()
        now = device.repairs

        assert original[0] == now[2]
        assert original[1] == now[0]
        assert original[2] == now[1]

        # But if I move it up again nothing should happen
        device.repairs[-1].move_down()
        device.repairs[-1].move_down()
        device.repairs[-1].move_down()
        device.repairs[-1].move_down()

        assert device.repairs[-1].order_index == 2

        # All other repairs should remain unchanged
        assert all(rep.order_index == 0 for rep in Repair.query.all() if rep.device != device)
