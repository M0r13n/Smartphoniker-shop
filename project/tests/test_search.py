from project.server.models import Device


class TestOrder:

    def test_create(self, db, sample_device, some_devices):
        assert "search" in dir(Device)

        # Normal search
        q = Device.query.filter(Device.name.like('iphone'))
        assert len(q.all()) == 0
        assert 'LIKE' in str(q)

        # Similarity
        result = Device.search_order_by_similarity('iPhone X')
        print(result, result.all())
        result = result.all()
        assert result[0].name == 'iPhone X'
