# -*- coding:utf-8 -*-

import unittest
from altair.app.ticketing.testing import DummyRequest
from pyramid.testing import DummyModel


class CancelPaymentMailViewletTest(unittest.TestCase):
    @staticmethod
    def _getTestTarget():
        from .. import pgw_credit_card
        return pgw_credit_card.cancel_payment_mail_viewlet

    def test_cancel_payment_mail_viewlet(self):
        """ cancel_payment_mail_viewletの正常系テスト """
        from pyramid.response import Response

        test_notice = u'test_notice'
        def mock_mail_data(arg1, arg2):
            return test_notice
        test_context = DummyModel(
            mail_data=mock_mail_data
        )
        request = DummyRequest()

        view_data = self._getTestTarget()(test_context, request)
        self.assertIsInstance(view_data, Response)
