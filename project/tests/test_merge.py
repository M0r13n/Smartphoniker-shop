from project.server.models import Device


class TestMerge:

    def test_name(self, sample_repair, sample_device, some_devices):
        merger = Device.merge([sample_device.id, ] + list(map(lambda d: d.id, some_devices)))
        assert merger.name == sample_device.name

        try:
            merger = Device.merge([sample_device.id, ])
            assert False
        except IndexError:
            assert True

    def test_image(self, sample_device, some_devices):
        merger = Device.merge([sample_device.id, ] + list(map(lambda d: d.id, some_devices)))
        assert merger.image == sample_device.image

    def test_is_tablet(self, sample_device, some_devices):
        merger = Device.merge([sample_device.id, ] + list(map(lambda d: d.id, some_devices)))
        assert merger.is_tablet == sample_device.is_tablet

    def test_repairs(self, sample_device, sample_repair, another_repair, another_device):
        reps = [sample_repair, another_repair]
        merger = Device.merge([sample_device.id, another_device.id])
        assert list(map(lambda x: x.name, sorted(merger.repairs, key=lambda r: r.id))) == list(map(lambda x: x.name, sorted(reps, key=lambda r: r.id)))

    def test_colors(self, sample_device, another_device, sample_color):
        colors = list(sample_device.colors) + list(another_device.colors)
        merger = Device.merge([sample_device.id, another_device.id])
        assert set(sorted(merger.colors, key=lambda r: r.id)) == set(sorted(colors, key=lambda r: r.id))

    def test_delete(self, sample_device, some_devices):
        Device.merge([sample_device.id, ] + list(map(lambda d: d.id, some_devices)))
        assert Device.query.count() == 1
