# -*- coding:utf-8 -*-

import unittest
import datetime
from altair.app.ticketing.testing import DummyRequest, _setup_db, _teardown_db
from altair.app.ticketing.core.testing import CoreTestMixin
from altair.app.ticketing.cart.testing import CartTestMixin
from pyramid.testing import DummyModel


class ConfirmViewletTest(unittest.TestCase):
    @staticmethod
    def _getTestTarget():
        from . import pgw_credit_card
        return pgw_credit_card.confirm_viewlet

    def test_confirm_viewlet(self):
        """ confirm_viewletの正常系テスト """
        test_context = {}
        request = DummyRequest()

        confirm_viewlet_dict = self._getTestTarget()(test_context, request)
        self.assertIsNotNone(confirm_viewlet_dict)
        self.assertIsNotNone(confirm_viewlet_dict['last4digits'])
        self.assertIsNotNone(confirm_viewlet_dict['expirationMonth'])
        self.assertIsNotNone(confirm_viewlet_dict['expirationYear'])


class CompletionViewlet(unittest.TestCase):
    @staticmethod
    def _getTestTarget():
        from . import pgw_credit_card
        return pgw_credit_card.completion_viewlet

    def test_completion_viewlet(self):
        """ completion_viewletの正常系テスト """
        test_context = {}
        request = DummyRequest()
        self._getTestTarget()(test_context, request)


class CompletionPaymentMailViewletTest(unittest.TestCase):
    @staticmethod
    def _getTestTarget():
        from . import pgw_credit_card
        return pgw_credit_card.completion_payment_mail_viewlet

    def test_completion_payment_mail_viewlet(self):
        """ completion_payment_mail_viewletの正常系テスト """
        test_context = {}
        request = DummyRequest()
        self._getTestTarget()(test_context, request)


class CancelPaymentMailViewletTest(unittest.TestCase):
    @staticmethod
    def _getTestTarget():
        from . import pgw_credit_card
        return pgw_credit_card.cancel_payment_mail_viewlet

    def test_cancel_payment_mail_viewlet(self):
        """ cancel_payment_mail_viewletの正常系テスト """
        test_context = {}
        request = DummyRequest()
        self._getTestTarget()(test_context, request)


class PaymentGatewayCreditCardPaymentPluginTest(unittest.TestCase, CoreTestMixin, CartTestMixin):
    def setUp(self):
        self.session = _setup_db([
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.orders.models',
            'altair.app.ticketing.cart.models',
        ])
        CoreTestMixin.setUp(self)

    def tearDown(self):
        self.session.remove()
        _teardown_db()

    @staticmethod
    def _getTestTarget():
        from . import pgw_credit_card
        return pgw_credit_card.PaymentGatewayCreditCardPaymentPlugin()

    def test_validate_order(self):
        """ validate_orderの正常系テスト """
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order_like = DummyModel(
            total_amount=100,
            payment_amount=100
        )
        plugin.validate_order(request, test_order_like)

    def test_validate_order_invalid_total_amount(self):
        """ validate_orderで総額が不正の場合のテスト """
        from altair.app.ticketing.payments.exceptions import OrderLikeValidationFailure
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order_like = DummyModel(
            total_amount=0,
            payment_amount=0
        )
        with self.assertRaises(OrderLikeValidationFailure):
            plugin.validate_order(request, test_order_like)

    def test_validate_order_invalid_payment_amount(self):
        """ validate_orderで支払額が不正の場合のテスト """
        from altair.app.ticketing.payments.exceptions import OrderLikeValidationFailure
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order_like = DummyModel(
            total_amount=100,
            payment_amount=-1
        )
        with self.assertRaises(OrderLikeValidationFailure):
            plugin.validate_order(request, test_order_like)

    def test_validate_order_cancellation(self):
        """ validate_order_cancellationの正常系テスト """
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order = {}
        now = datetime.datetime.now()
        plugin.validate_order_cancellation(request, test_order, now)

    def test_prepare(self):
        """ prepareの正常系テスト """
        from pyramid.httpexceptions import HTTPFound
        plugin = self._getTestTarget()


        def mock_route_url(arg1):
            return 'http://dummy_route_url'

        request = DummyRequest(
            session={},
            route_url=mock_route_url
        )
        test_auth_model = u'test_auth_model'
        test_cart = DummyModel(
            sales_segment=DummyModel(
                auth3d_notice=test_auth_model
            )
        )
        http_exception = plugin.prepare(request, test_cart)
        self.assertIsInstance(http_exception, HTTPFound)
        self.assertEqual(request.session['altair.app.ticketing.payments.auth3d_notice'], test_auth_model)

    def test_finish(self):
        """ finishの正常系テスト """
        from altair.app.ticketing.core.models import SalesSegmentGroup, SalesSegment
        from altair.app.ticketing.cart.models import CartSetting
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_stock_types = self._create_stock_types(1)
        test_stocks = self._create_stocks(test_stock_types)
        test_products = self._create_products(test_stocks)
        test_sales_segment_group = SalesSegmentGroup(event=self.event)
        test_sales_segment = SalesSegment(performance=self.performance, sales_segment_group=test_sales_segment_group)
        test_pdmp = self._create_payment_delivery_method_pairs(test_sales_segment_group)[0]
        test_cart_setting = CartSetting(type='standard')
        test_cart = self._create_cart(
            zip(test_products, [1]),
            test_sales_segment,
            test_cart_setting,
            pdmp=test_pdmp
        )

        order = plugin.finish(request, test_cart)
        self.assertIsNotNone(order)
        self.assertIsNotNone(order.paid_at)
        self.assertIsNotNone(test_cart.finished_at)

    def test_finish2(self):
        """ finish2の正常系テスト """
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order = {}
        plugin.finish2(request, test_order)

    def test_sales(self):
        """ salesの正常系テスト """
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_cart = {}
        plugin.sales(request, test_cart)

    def test_finished(self):
        """ finishedの正常系テスト """
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order = {}
        plugin.finished(request, test_order)

    def test_cancel(self):
        """ cancelの正常系テスト """
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order = {}
        now = datetime.datetime.now()
        plugin.cancel(request, test_order, now)

    def test_refresh(self):
        """ refreshの正常系テスト """
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order = {}
        plugin.refresh(request, test_order)

    def test_refund(self):
        """ refundの正常系テスト """
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order = {}
        test_refund_record = {}
        plugin.refund(request, test_order, test_refund_record)

    def test_get_order_info(self):
        """ get_order_infoの正常系テスト """
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order = {}
        plugin.get_order_info(request, test_order)


class PaymentGatewayCreditCardViewTest(unittest.TestCase):
    def setUp(self):
        from pyramid import testing
        from altair.app.ticketing.payments.interfaces import ICartInterface

        def get_success_url_mock(request):
            return 'http://example.com'

        self.config = testing.setUp()
        self.config.registry.utilities.register([], ICartInterface, "", DummyModel(
            get_success_url=get_success_url_mock
        ))

    def tearDown(self):
        from pyramid import testing
        testing.tearDown()

    @staticmethod
    def _getTestTarget(*args, **kwargs):
        from . import pgw_credit_card
        return pgw_credit_card.PaymentGatewayCreditCardView(*args, **kwargs)

    def test_show_card_form(self):
        """ show_card_formの正常系テスト """
        request = DummyRequest(
            session={}
        )
        test_view = self._getTestTarget(request)

        card_form_dict = test_view.show_card_form()
        self.assertIsNotNone(card_form_dict)
        self.assertIsNotNone(card_form_dict.get('form'))
        self.assertIsNone(card_form_dict.get('latest_card_info'))


    def test_process_card_token(self):
        """ process_card_tokenの正常系テスト """
        from pyramid.httpexceptions import HTTPFound
        request = DummyRequest(
            session={},
            registry=self.config.registry
        )
        test_view = self._getTestTarget(request)

        http_exception = test_view.process_card_token()
        self.assertIsInstance(http_exception, HTTPFound)
