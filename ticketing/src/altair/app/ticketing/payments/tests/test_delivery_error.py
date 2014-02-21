import mock
import unittest
from pyramid import testing
from altair.app.ticketing.testing import DummyRequest

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
        self.config.add_subscriber(
            self.delivery_error_event_subscriber,
            'altair.app.ticketing.payments.events.DeliveryErrorEvent')

    def test_delivery_error(self):
        from altair.app.ticketing.payments.payment import Payment
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

class TestCancelOnDeliveryError(unittest.TestCase):
    def _getTarget(self):
        from ..events import cancel_on_delivery_error
        return cancel_on_delivery_error

    def _callFUT(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    @mock.patch('transaction.commit')
    @mock.patch('sqlahelper.get_session')
    def test_it(self, get_session_fn, commit_fn):
        from ..events import DeliveryErrorEvent
        order = mock.Mock()
        event = DeliveryErrorEvent(
            testing.DummyModel(),
            DummyRequest(),
            order
            )
        self._callFUT(event)
        order.cancel.assert_called_once_with(event.request)
        get_session_fn.assert_called_once_with()
        commit_fn.assert_called_once_with()
