# -*- coding:utf-8 -*-

import unittest
import datetime
from altair.app.ticketing.testing import DummyRequest
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
        self._getTestTarget()(test_context, request)


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


class PaymentGatewayCreditCardPaymentPluginTest(unittest.TestCase):
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
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_cart = {}
        plugin.finish(request, test_cart)

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
