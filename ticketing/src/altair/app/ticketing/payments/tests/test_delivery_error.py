import mock
import unittest
from pyramid import testing
from altair.app.ticketing.testing import DummyRequest
from zope.interface import directlyProvides

class DummyPaymentPlugin(object):
    def __init__(self, dummy_order):
        self.dummy_order = dummy_order

    def prepare(self, request, cart):
        pass

    def finish(self, request, cart):
        return self.dummy_order

    def sales(self, request, cart):
        pass

    def finished(self, request, order):
        pass

    def cancel(self, request, order):
        pass

    def refresh(self, request, order):
        pass


class FailingDeliveryPlugin(object):
    def __init__(self, exc_class):
        self.exc_class = exc_class

    def prepare(self, request, cart):
        pass

    def finish(self, request, cart):
        raise self.exc_class("OOPS")

    def finished(self, request, order):
        pass

    def refresh(self, request, order):
        pass

class TestDeliveryError(unittest.TestCase):
    class Exception(Exception):
        pass

    def setUp(self):
        self.dummy_order = testing.DummyModel(
            performance=testing.DummyModel(
                event=testing.DummyModel(
                    organization_id=0
                    )
                )
            )
        self.config = testing.setUp()
        self.config.include('altair.app.ticketing.payments')
        self.config.add_delivery_plugin(FailingDeliveryPlugin(self.Exception), 0)
        self.config.add_payment_plugin(DummyPaymentPlugin(self.dummy_order), 0)
        self.delivery_error_event_subscriber = mock.Mock()

    def test_delivery_error(self):
        from altair.app.ticketing.payments.payment import Payment
        from altair.app.ticketing.payments.interfaces import IPaymentCart
        dummy_session = mock.Mock()
        cart = testing.DummyModel(
            performance=testing.DummyModel(
                event_id=0
                ),
            sales_segment=testing.DummyModel(),
            payment_delivery_pair=testing.DummyModel(
                delivery_method=testing.DummyModel(
                    delivery_plugin_id=0
                    ),
                payment_method=testing.DummyModel(
                    payment_plugin_id=0
                    )
                )
            )
        directlyProvides(cart, IPaymentCart)
        request = DummyRequest()
        payment = Payment(cart, request, session=dummy_session)
        raised_exception = None
        with self.assertRaises(self.Exception) as ctx:
            payment.call_payment()
        raised_exception = ctx.exception
        dummy_session.add.assert_called_with(self.dummy_order)
        self.assertEqual(self.delivery_error_event_subscriber.call_args[0][0].exception, raised_exception)
        self.assertEqual(self.delivery_error_event_subscriber.call_args[0][0].request, request)
        self.assertEqual(self.delivery_error_event_subscriber.call_args[0][0].order, self.dummy_order)
