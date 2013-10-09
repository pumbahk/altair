# -*- coding:utf-8 -*-

import unittest
import mock
from pyramid import testing
from altair.app.ticketing.testing import _setup_db, _teardown_db, DummyRequest

model_dependencies = [
    'altair.app.ticketing.models',
    'altair.app.ticketing.core.models',
    'altair.app.ticketing.users.models',
    'altair.app.ticketing.cart.models',
    'altair.app.ticketing.lots.models',
]

class get_preparerTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.session = _setup_db(model_dependencies)

    @classmethod
    def tearDownClass(cls):
        _teardown_db()

    def setUp(self):
        self.session.remove()
        self.config = testing.setUp()

    def tearDown(self):
        import transaction
        transaction.abort()
        testing.tearDown()

    def _getTarget(self):
        from ..payment import get_preparer
        return get_preparer

    def _callFUT(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_iface(self):
        from zope.interface.verify import verifyObject
        from ..interfaces import IPaymentPreparerFactory
        verifyObject(IPaymentPreparerFactory, self._getTarget())

    def test_with_payment_delivery_plugin(self):
        """ payment_delivery_pluginが取得できた場合
        """
        from ..interfaces import IPaymentDeliveryPlugin
        from ..interfaces import IPaymentPreparer
        request = DummyRequest()

        payment_delivery_pair = testing.DummyModel(
            payment_method=testing.DummyModel(payment_plugin_id=1),
            delivery_method=testing.DummyModel(delivery_plugin_id=2),
        )

        marker = testing.DummyResource()
        request.registry.utilities.register([], IPaymentDeliveryPlugin,
            "payment-1:delivery-2", marker)

        result = self._callFUT(request, payment_delivery_pair)

        self.assertEqual(result, marker)
        self.assertTrue(IPaymentPreparer.providedBy(marker))

    def test_with_payment_plugin(self):
        """ payment_pluginが取得できた場合
        """
        from ..interfaces import IPaymentPlugin
        from ..interfaces import IPaymentPreparer
        request = DummyRequest()

        payment_delivery_pair = testing.DummyModel(
            payment_method=testing.DummyModel(payment_plugin_id=1),
            delivery_method=testing.DummyModel(delivery_plugin_id=2),
        )

        marker = testing.DummyResource()
        request.registry.utilities.register([], IPaymentPlugin,
            "payment-1", marker)

        result = self._callFUT(request, payment_delivery_pair)

        self.assertEqual(result, marker)
        self.assertTrue(IPaymentPreparer.providedBy(marker))

    def test_no_plugins(self):
        """ 取得できなかった場合
        """

        request = DummyRequest()

        payment_delivery_pair = testing.DummyModel(
            payment_method=testing.DummyModel(payment_plugin_id=None),
            delivery_method=testing.DummyModel(delivery_plugin_id=None),
        )

        result = self._callFUT(request, payment_delivery_pair)

        self.assertIsNone(result)

class PaymentTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.session = _setup_db(model_dependencies)

    @classmethod
    def tearDownClass(cls):
        _teardown_db()

    def setUp(self):
        self.session.remove()

    def tearDown(self):
        import transaction
        transaction.abort()


    def _getTarget(self):
        from ..payment import Payment
        return Payment

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_prepare(self):
        request = DummyRequest()
        sales_segment = testing.DummyModel()
        cart = testing.DummyModel(sales_segment=sales_segment)
        target = self._getTarget()
        result = target(cart, request)

        self.assertEqual(result.request, request)
        self.assertEqual(result.cart, cart)
        self.assertEqual(result.sales_segment, sales_segment)

    @mock.patch('altair.app.ticketing.payments.payment.get_preparer')
    def test_call_prepare(self, get_preparer):
        preparer = mock.Mock()
        preparer.prepare.return_value = None
        get_preparer.return_value = preparer

        request = DummyRequest()
        payment_delivery_pair = testing.DummyModel()
        cart = testing.DummyModel(payment_delivery_pair=payment_delivery_pair,
            sales_segment=None)

        target = self._makeOne(cart, request)
        result = target.call_prepare()

        self.assertIsNone(result)
        preparer.prepare.assert_called_with(request, cart)


    @mock.patch("altair.app.ticketing.payments.payment.get_preparer")
    @mock.patch("transaction.commit")
    def test_call_payment_with_peymend_delivery_plugin(self, mock_commit, mock_get_preparer):
        from altair.app.ticketing.core.models import Order, Performance, Event, Organization
        order = Order(total_amount=10, system_fee=1234,
            transaction_fee=234, delivery_fee=234,
            performance=Performance(event=Event(organization=Organization(short_name="this-is-test", id=11111))))
        self.session.add(order)
        self.session.flush()
        payment_delivery_plugin = mock.Mock()
        payment_delivery_plugin.finish.return_value = order

        request = DummyRequest()
        payment_delivery_pair = testing.DummyModel()
        cart = testing.DummyModel(payment_delivery_pair=payment_delivery_pair,
            sales_segment=None,
            performance=order.performance)

        target = self._makeOne(cart, request)
        target.get_plugins = lambda pair: (payment_delivery_plugin, None, None)

        result = target.call_payment()


        self.assertEqual(result, order)
        self.assertEqual(cart.order, order)
        self.assertEqual(order.organization_id, order.performance.event.organization.id)
        payment_delivery_plugin.finish.assert_called_with(request, cart)
        mock_commit.assert_called_with()
        mock_get_preparer.assert_called_with(request, payment_delivery_pair)

    @mock.patch("altair.app.ticketing.payments.payment.get_preparer")
    @mock.patch("transaction.commit")
    def test_call_payment_with_peymend_plugin_delivery_plugin(self, mock_commit, mock_get_preparer):
        from altair.app.ticketing.core.models import Order, Performance, Event, Organization
        order = Order(total_amount=10, system_fee=1234,
            transaction_fee=234, delivery_fee=234,
            performance=Performance(event=Event(organization=Organization(short_name="this-is-test", id=11111))))
        self.session.add(order)
        self.session.flush()
        payment_plugin = mock.Mock()
        payment_plugin.finish.return_value = order
        delivery_plugin = mock.Mock()

        request = DummyRequest()
        payment_delivery_pair = testing.DummyModel()
        cart = testing.DummyModel(payment_delivery_pair=payment_delivery_pair,
            sales_segment=None,
            performance=order.performance)

        target = self._makeOne(cart, request)
        target.get_plugins = lambda pair: (None, payment_plugin, delivery_plugin)

        result = target.call_payment()


        self.assertEqual(result, order)
        self.assertEqual(cart.order, order)
        self.assertEqual(order.organization_id, order.performance.event.organization.id)
        payment_plugin.finish.assert_called_with(request, cart)
        delivery_plugin.finish.assert_called_with(request, cart)
        mock_commit.assert_called_with()
        mock_get_preparer.assert_called_with(request, payment_delivery_pair)

    @mock.patch("altair.app.ticketing.payments.payment.get_preparer")
    @mock.patch("transaction.commit")
    def test_call_payment_with_delivery_error(self, mock_commit, mock_get_preparer):
        from altair.app.ticketing.core.models import Order, Performance, Event, Organization
        from altair.app.ticketing.payments.exceptions import PaymentPluginException
        event_id = 768594
        order_no = "error-order"
        order = Order(total_amount=10, system_fee=1234,
            order_no=order_no,
            transaction_fee=234, delivery_fee=234,
            performance=Performance(event=Event(id=event_id, organization=Organization(short_name="this-is-test", id=11111))))
        self.session.add(order)
        self.session.flush()

        payment_plugin = mock.Mock()
        payment_plugin.finish.return_value = order
        delivery_plugin = mock.Mock()
        e = PaymentPluginException('', '', None)
        delivery_plugin.finish.side_effect = e

        request = DummyRequest()
        payment_delivery_pair = testing.DummyModel()
        cart = testing.DummyModel(payment_delivery_pair=payment_delivery_pair,
            sales_segment=None,
            performance=order.performance)

        target = self._makeOne(cart, request)
        target.get_plugins = lambda pair: (None, payment_plugin, delivery_plugin)

        self.assertRaises(PaymentPluginException, target.call_payment)

        # エラー発生時でもコミットされること。
        mock_commit.assert_called_with()
        mock_get_preparer.assert_called_with(request, payment_delivery_pair)

# class on_delivery_errorTests(unittest.TestCase):
#     def _callFUT(self, *args, **kwargs):
#         from ..payment import on_delivery_error
#         return on_delivery_error(*args, **kwargs)

#     @mock.patch('traceback.print_exception')
#     @mock.patch('sys.exc_info')
#     def test_it(self, mock_exc_info, mock_print_exception):
#         exc_info = object(), object(), object()
#         mock_exc_info.return_value = exc_info
#         request = DummyRequest()
#         e = mock.Mock()
#         order_no = "error-order"
#         event_id = 11111
#         cart = testing.DummyModel(event_id=event_id)
#         order = mock.Mock(order_no=order_no, cart=cart)


#        self._callFUT(e, request, order)

#        order.cancel.assert_called_with(request)
#        mock_exc_info.assert_called_with()
        
