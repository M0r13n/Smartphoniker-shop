from sqlalchemy.exc import IntegrityError

from project.server.models import Manufacturer, Repair, Device
from project.server.models.image import Default, Image


class TestImage:

    def test_all_classes_have_mixins(self):
        assert 'get_image_path' in dir(Manufacturer)
        assert 'image_id' in dir(Manufacturer)
        assert 'get_image_path' in dir(Device)
        assert 'image_id' in dir(Device)
        assert 'get_image_path' in dir(Repair)
        assert 'image_id' in dir(Repair)

    def test_default_images_are_none_by_default(self, db, sample_repair, sample_device, sample_manufacturer, sample_image):
        assert sample_repair.get_image_path() is None
        assert sample_repair.image is None
        assert sample_device.get_image_path() is None
        assert sample_device.image is None
        assert sample_manufacturer.get_image_path() is None
        assert sample_manufacturer.image is None

    def test_default_images_can_be_set(self, db, sample_repair, sample_device, sample_manufacturer, sample_image):
        sample_image.repair_default = Default.true
        sample_image.save()
        assert sample_repair.get_image_path() is not None
        assert sample_repair.get_image() is sample_image
        assert sample_device.get_image_path() is None
        assert sample_manufacturer.get_image_path() is None

        sample_image.device_default = Default.true
        sample_image.save()
        assert sample_repair.get_image_path() is not None
        assert sample_repair.get_image() is sample_image
        assert sample_device.get_image_path() is not None
        assert sample_device.get_image() is sample_image
        assert sample_manufacturer.get_image_path() is None

        sample_image.manufacturer_default = Default.true
        sample_image.save()
        assert sample_repair.get_image_path() is not None
        assert sample_repair.get_image() is sample_image
        assert sample_device.get_image_path() is not None
        assert sample_device.get_image() is sample_image
        assert sample_manufacturer.get_image_path() is not None
        assert sample_manufacturer.get_image() is sample_image

    def test_that_only_one_default_is_possible(self, db, sample_image):
        sample_image.repair_default = Default.true
        sample_image.save()

        another_image = Image.create(name="Wurst", path="Wurst")

        try:
            another_image.repair_default = Default.true
            another_image.save()
            assert False
        except IntegrityError:
            return True
