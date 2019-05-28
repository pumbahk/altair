# -*- coding:utf-8 -*-

import unittest
from altair.app.ticketing.testing import DummyRequest, _setup_db, _teardown_db
import mock
from pyramid.testing import DummyModel


class ConfirmViewletTest(unittest.TestCase):
    @staticmethod
    def _getTestTarget():
        from .. import pgw_credit_card
        return pgw_credit_card.confirm_viewlet

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.get_cart')
    def test_confirm_viewlet(self, get_cart):
        """ confirm_viewletの正常系テスト """
        test_context = {}
        test_order_no = u'TEST000001'
        test_safe_card_info = {
            u'last4digits': u'1234',
            u'expirationMonth': u'2100',
            u'expirationYear': u'04'
        }
        request = DummyRequest(
            session={
                u'pgw_safe_card_info_{}'.format(test_order_no): test_safe_card_info
            }
        )
        get_cart.return_value = DummyModel(
            order_no=test_order_no
        )

        confirm_viewlet_dict = self._getTestTarget()(test_context, request)
        self.assertIsNotNone(confirm_viewlet_dict)
        self.assertEqual(confirm_viewlet_dict[u'last4digits'], test_safe_card_info[u'last4digits'])
        self.assertEqual(confirm_viewlet_dict[u'expirationMonth'], test_safe_card_info[u'expirationMonth'])
        self.assertEqual(confirm_viewlet_dict[u'expirationYear'], test_safe_card_info[u'expirationYear'])
