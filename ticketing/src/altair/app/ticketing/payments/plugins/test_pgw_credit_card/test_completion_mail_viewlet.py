# -*- coding:utf-8 -*-

import unittest
from altair.app.ticketing.testing import DummyRequest, _setup_db, _teardown_db


class CompletionPaymentMailViewletTest(unittest.TestCase):
    @staticmethod
    def _getTestTarget():
        from .. import pgw_credit_card
        return pgw_credit_card.completion_payment_mail_viewlet

    def test_completion_payment_mail_viewlet(self):
        """ completion_payment_mail_viewletの正常系テスト """
        test_context = {}
        request = DummyRequest()
        self._getTestTarget()(test_context, request)
