# -*- coding:utf-8 -*-

import unittest
import datetime
from altair.app.ticketing.testing import DummyRequest


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
        test_order_like = {}
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
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_cart = {}
        plugin.prepare(request, test_cart)

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
    @staticmethod
    def _getTestTarget():
        from . import pgw_credit_card
        return pgw_credit_card.PaymentGatewayCreditCardView()

    def test_show_card_form(self):
        """ show_card_formの正常系テスト """
        test_view = self._getTestTarget()
        test_view.show_card_form()

    def test_process_card_token(self):
        """ process_card_tokenの正常系テスト """
        test_view = self._getTestTarget()
        test_view.process_card_token()
