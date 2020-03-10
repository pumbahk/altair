# -*- coding:utf-8 -*-

import unittest
from altair.app.ticketing.testing import DummyRequest
from pyramid.testing import DummyModel


class CompletionPaymentMailViewletTest(unittest.TestCase):
    @staticmethod
    def _getTestTarget():
        from .. import pgw_credit_card
        return pgw_credit_card.completion_payment_mail_viewlet

    def test_completion_payment_mail_viewlet(self):
        """ completion_payment_mail_viewletの正常系テスト """
        test_notice = u'test_notice'
        test_order = DummyModel()
        def mock_mail_data(arg1, arg2):
            return test_notice
        test_context = DummyModel(
            mail_data=mock_mail_data,
            order=test_order
        )
        request = DummyRequest()

        view_data = self._getTestTarget()(test_context, request)
        self.assertIsNotNone(view_data)
        self.assertEqual(view_data['notice'], test_notice)
