# -*- coding:utf-8 -*-

import unittest
from altair.app.ticketing.testing import DummyRequest, _setup_db, _teardown_db


class CompletionViewlet(unittest.TestCase):
    @staticmethod
    def _getTestTarget():
        from .. import pgw_credit_card
        return pgw_credit_card.completion_viewlet

    def test_completion_viewlet(self):
        """ completion_viewletの正常系テスト """
        test_context = {}
        request = DummyRequest()

        complete_viewlet_dict = self._getTestTarget()(test_context, request)
        self.assertIsNotNone(complete_viewlet_dict)
