# -*- coding:utf-8 -*-

import unittest
from altair.app.ticketing.testing import DummyRequest, _setup_db, _teardown_db


class CancelPaymentMailViewletTest(unittest.TestCase):
    @staticmethod
    def _getTestTarget():
        from .. import pgw_credit_card
        return pgw_credit_card.cancel_payment_mail_viewlet

    def test_cancel_payment_mail_viewlet(self):
        """ cancel_payment_mail_viewletの正常系テスト """
        test_context = {}
        request = DummyRequest()
        self._getTestTarget()(test_context, request)
