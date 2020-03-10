# -*- coding:utf-8 -*-

import unittest
import mock
from pyramid import testing
from datetime import datetime
from zope.interface import directlyProvides
from altair.app.ticketing.testing import _setup_db, _teardown_db, DummyRequest

model_dependencies = [
    'altair.app.ticketing.models',
    'altair.app.ticketing.orders.models',
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
        from ..api import get_preparer
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
        from altair.app.ticketing.payments.interfaces import IPaymentCart
        request = DummyRequest()
        sales_segment = testing.DummyModel()
        cart = testing.DummyModel(sales_segment=sales_segment)
        directlyProvides(cart, IPaymentCart)
        target = self._getTarget()
        result = target(cart, request)

        self.assertEqual(result.request, request)
        self.assertEqual(result.cart, cart)
        self.assertEqual(result.sales_segment, sales_segment)

    def test_call_prepare(self):
        from altair.app.ticketing.payments.interfaces import IPaymentCart
        preparer = mock.Mock()
        preparer.prepare.return_value = None
        mock_get_preparer = mock.Mock()
        mock_get_preparer.return_value = preparer

        request = DummyRequest()
        payment_delivery_pair = testing.DummyModel()
        cart = testing.DummyModel(payment_delivery_pair=payment_delivery_pair,
            sales_segment=None)
        directlyProvides(cart, IPaymentCart)
        session = mock.Mock()

        target = self._makeOne(cart, request, session)
        target.get_preparer = mock_get_preparer
        result = target.call_prepare()

        self.assertIsNone(result)
        preparer.prepare.assert_called_with(request, cart)

    @mock.patch("transaction.commit")
    def test_call_payment_with_peymend_delivery_plugin(self, mock_commit):
        from altair.app.ticketing.core.models import Performance, Event, Organization, PointUseTypeEnum
        from altair.app.ticketing.orders.models import Order
        from altair.app.ticketing.payments.interfaces import IPaymentCart
        order = Order(
            total_amount=10, system_fee=1234,
            transaction_fee=234, delivery_fee=234,
            issuing_start_at=datetime(1970, 1, 1),
            issuing_end_at=datetime(1970, 1, 1),
            payment_start_at=datetime(1970, 1, 1),
            payment_due_at=datetime(1970, 1, 1),
            performance=Performance(
                event=Event(
                    organization=Organization(
                        short_name="this-is-test",
                        id=11111
                        )
                    )
                )
            )
        self.session.add(order)
        self.session.flush()
        payment_delivery_plugin = mock.Mock()
        payment_delivery_plugin.finish.return_value = order
        mock_get_preparer = mock.Mock()

        request = DummyRequest()
        payment_delivery_pair = testing.DummyModel()
        cart = testing.DummyModel(payment_delivery_pair=payment_delivery_pair,
            sales_segment=None,
            performance=order.performance,
            point_use_type=PointUseTypeEnum.NoUse)
        directlyProvides(cart, IPaymentCart)
        session = mock.Mock()

        target = self._makeOne(cart, request, session)
        target._get_plugins = lambda pair: (payment_delivery_plugin, None, None)
        target.get_preparer = mock_get_preparer

        result = target.call_payment()


        self.assertEqual(result, order)
        self.assertEqual(cart.order, order)
        self.assertEqual(order.organization_id, order.performance.event.organization.id)
        payment_delivery_plugin.finish.assert_called_with(request, cart)
        self.assertFalse(mock_commit.called)
        mock_get_preparer.assert_called_with(request, payment_delivery_pair)

    @mock.patch("transaction.commit")
    def test_call_payment_with_peymend_plugin_delivery_plugin(self, mock_commit):
        from altair.app.ticketing.core.models import Performance, Event, Organization, PointUseTypeEnum
        from altair.app.ticketing.orders.models import Order
        from altair.app.ticketing.payments.interfaces import IPaymentCart
        order = Order(
            total_amount=10, system_fee=1234,
            transaction_fee=234, delivery_fee=234,
            issuing_start_at=datetime(1970, 1, 1),
            issuing_end_at=datetime(1970, 1, 1),
            payment_start_at=datetime(1970, 1, 1),
            payment_due_at=datetime(1970, 1, 1),
            performance=Performance(
                event=Event(
                    organization=Organization(
                        short_name="this-is-test",
                        id=11111
                        )
                    )
                )
            )
        self.session.add(order)
        self.session.flush()
        payment_plugin = mock.Mock()
        payment_plugin.finish.return_value = order
        delivery_plugin = mock.Mock()
        mock_get_preparer = mock.Mock()

        request = DummyRequest()
        payment_delivery_pair = testing.DummyModel()
        cart = testing.DummyModel(payment_delivery_pair=payment_delivery_pair,
            sales_segment=None,
            performance=order.performance,
            point_use_type=PointUseTypeEnum.NoUse)
        directlyProvides(cart, IPaymentCart)
        session = mock.Mock()

        target = self._makeOne(cart, request, session)
        target.get_preparer = mock_get_preparer
        target._get_plugins = lambda pair: (None, payment_plugin, delivery_plugin)

        result = target.call_payment()


        self.assertEqual(result, order)
        self.assertEqual(cart.order, order)
        self.assertEqual(order.organization_id, order.performance.event.organization.id)
        payment_plugin.finish.assert_called_with(request, cart)
        delivery_plugin.finish.assert_called_with(request, cart)
        self.assertFalse(mock_commit.called)
        mock_get_preparer.assert_called_with(request, payment_delivery_pair)

    @mock.patch("transaction.commit")
    def test_call_payment_with_delivery_error(self, mock_commit):
        from altair.app.ticketing.core.models import Performance, Event, Organization, PointUseTypeEnum
        from altair.app.ticketing.orders.models import Order
        from altair.app.ticketing.payments.exceptions import PaymentPluginException
        from altair.app.ticketing.payments.interfaces import IPaymentCart
        event_id = 768594
        order_no = "error-order"
        order = Order(
            total_amount=10, system_fee=1234,
            order_no=order_no,
            transaction_fee=234, delivery_fee=234,
            issuing_start_at=datetime(1970, 1, 1),
            issuing_end_at=datetime(1970, 1, 1),
            payment_start_at=datetime(1970, 1, 1),
            payment_due_at=datetime(1970, 1, 1),
            performance=Performance(
                event=Event(
                    id=event_id,
                    organization=Organization(
                        short_name="this-is-test",
                        id=11111
                        )
                    )
                )
            )
        self.session.add(order)
        self.session.flush()

        payment_plugin = mock.Mock()
        payment_plugin.finish.return_value = order
        delivery_plugin = mock.Mock()
        e = PaymentPluginException('', '', None)
        delivery_plugin.finish.side_effect = e
        mock_get_preparer = mock.Mock()

        request = DummyRequest()
        payment_delivery_pair = testing.DummyModel()
        cart = testing.DummyModel(payment_delivery_pair=payment_delivery_pair,
            sales_segment=None,
            performance=order.performance,
            point_use_type=PointUseTypeEnum.NoUse,
            order_no=order_no)
        directlyProvides(cart, IPaymentCart)
        session = mock.Mock()

        target = self._makeOne(cart, request, session)
        target._get_plugins = lambda pair: (None, payment_plugin, delivery_plugin)
        target.get_preparer = mock_get_preparer

        self.assertRaises(PaymentPluginException, target.call_payment)

        self.assertFalse(mock_commit.called)
        mock_get_preparer.assert_called_with(request, payment_delivery_pair)

    def test_call_get_auth_success(self):
        """ call_get_authの正常系テスト 処理成功 """
        from altair.app.ticketing.payments.interfaces import IPaymentCart
        preparer = mock.Mock()
        preparer.get_auth.return_value = None
        mock_get_preparer = mock.Mock()
        mock_get_preparer.return_value = preparer

        request = DummyRequest()
        payment_delivery_pair = testing.DummyModel()
        cart = testing.DummyModel(payment_delivery_pair=payment_delivery_pair,
                                  sales_segment=None)
        test_user_id = u'test_user_id'
        test_email = u'test@example.com'
        directlyProvides(cart, IPaymentCart)
        session = mock.Mock()

        target = self._makeOne(cart, request, session)
        target.get_preparer = mock_get_preparer
        result = target.call_get_auth(test_user_id, test_email)

        self.assertIsNone(result)
        preparer.get_auth.assert_called_with(request, cart, test_user_id, test_email)

    def test_call_get_auth_error(self):
        """ call_get_authの異常系テスト 無視できないエラー """
        from altair.app.ticketing.payments.interfaces import IPaymentCart
        from altair.app.ticketing.payments.exceptions import PaymentPluginException
        preparer = mock.Mock()
        preparer.get_auth.side_effect = PaymentPluginException('', '', '')
        mock_get_preparer = mock.Mock()
        mock_get_preparer.return_value = preparer

        request = DummyRequest()
        payment_delivery_pair = testing.DummyModel()
        cart = testing.DummyModel(
            payment_delivery_pair=payment_delivery_pair,
            sales_segment=None,
            order_no=u'TEST00001'
        )
        test_user_id = u'test_user_id'
        test_email = u'test@example.com'
        directlyProvides(cart, IPaymentCart)
        session = mock.Mock()

        target = self._makeOne(cart, request, session)
        target.get_preparer = mock_get_preparer
        with self.assertRaises(PaymentPluginException):
            target.call_get_auth(test_user_id, test_email)

    def test_call_get_auth_ignorable_error(self):
        """ call_get_authの異常系テスト 無視可能なエラー """
        from altair.app.ticketing.payments.interfaces import IPaymentCart
        from altair.app.ticketing.payments.exceptions import PaymentPluginException
        preparer = mock.Mock()
        preparer.get_auth.side_effect = PaymentPluginException('', '', '', ignorable=True)
        mock_get_preparer = mock.Mock()
        mock_get_preparer.return_value = preparer

        request = DummyRequest()
        payment_delivery_pair = testing.DummyModel()
        cart = testing.DummyModel(
            payment_delivery_pair=payment_delivery_pair,
            sales_segment=None,
            order_no=u'TEST00001'
        )
        test_user_id = u'test_user_id'
        test_email = u'test@example.com'
        directlyProvides(cart, IPaymentCart)
        session = mock.Mock()

        target = self._makeOne(cart, request, session)
        target.get_preparer = mock_get_preparer
        with self.assertRaises(PaymentPluginException):
            target.call_get_auth(test_user_id, test_email)

    def test_call_get_auth_without_preparer(self):
        """ call_get_authの異常系テスト preparerが存在しない """
        from altair.app.ticketing.payments.interfaces import IPaymentCart
        mock_get_preparer = mock.Mock()
        mock_get_preparer.return_value = None

        request = DummyRequest()
        payment_delivery_pair = testing.DummyModel()
        cart = testing.DummyModel(payment_delivery_pair=payment_delivery_pair,
                                  sales_segment=None)
        test_user_id = u'test_user_id'
        test_email = u'test@example.com'
        directlyProvides(cart, IPaymentCart)
        session = mock.Mock()

        target = self._makeOne(cart, request, session)
        target.get_preparer = mock_get_preparer
        with self.assertRaises(Exception):
            target.call_get_auth(test_user_id, test_email)

    def test_call_get_auth_without_implement(self):
        """ call_get_authの正常系テスト プラグインにget_auth実装なし """
        from altair.app.ticketing.payments.interfaces import IPaymentCart
        mock_get_preparer = mock.Mock()
        mock_get_preparer.return_value = testing.DummyModel()

        request = DummyRequest()
        payment_delivery_pair = testing.DummyModel()
        cart = testing.DummyModel(payment_delivery_pair=payment_delivery_pair,
                                  sales_segment=None)
        test_user_id = u'test_user_id'
        test_email = u'test@example.com'
        directlyProvides(cart, IPaymentCart)
        session = mock.Mock()

        target = self._makeOne(cart, request, session)
        target.get_preparer = mock_get_preparer
        result = target.call_get_auth(test_user_id, test_email)

        self.assertIsNone(result)

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
        
