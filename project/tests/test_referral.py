from project.server.config import RAIDER_CONFIG
from project.server.shop.actions import track_payment, perform_post_complete_actions


class TestReferral:

    def test_raider_config(self, app):
        assert RAIDER_CONFIG['host']
        assert RAIDER_CONFIG['track_token']
        assert RAIDER_CONFIG['default_currency']
        assert app.config['AFFILIATE_BONUS']

    def test_track_payment(self):
        import raider_reporter.reporter as r
        _orig = r.RaiderReporter.track_payment
        r.RaiderReporter.track_payment = lambda *args, **kwargs: True
        assert track_payment("A", 123.0, "sdf")
        r.RaiderReporter.track_payment = _orig

    def test_track_payment_returns_false_but_exception_is_handled(self):
        assert not track_payment("1234", 12.0)

    def test_order_post_actions(self, db):
        import project.server.models.order as order
        _orig = order.Order.notify
        order.Order.notify = lambda _: True

        # test that a normal order call track_payment
        # this is false because the track_id is not set for raider does not work and raises an exception
        o = order.Order()
        assert not perform_post_complete_actions(o)

        # in this case it's just skipped
        o.kva = True
        assert perform_post_complete_actions(o)
        order.Order.notify = _orig
