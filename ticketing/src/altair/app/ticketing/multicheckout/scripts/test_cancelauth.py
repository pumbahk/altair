# -*- coding:utf-8 -*-
from datetime import datetime
import unittest
import mock
from pyramid import testing
from altair.multicheckout.interfaces import IMulticheckoutSettingFactory
from altair.app.ticketing.testing import _setup_db, _teardown_db

# class Testcancel_auth(unittest.TestCase):
#     def _callFUT(self, *args, **kwargs):
#         from . cancelauth import cancel_auth
#         return cancel_auth(*args, **kwargs)

#     @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.m.MultiCheckoutOrderStatus')
#     @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.api.checkout_auth_cancel')
#     def test_it(self, mock_session, mock_cancel):
#         statuses = [
#             # CancelFilterでキャンセル不可能
#             # オーソリOKでないのでキャンセル不可能
#             # オーソリOK,CancelFilterにもひっかからないので、cancelされる
#         ]

#         request = testing.DummyRequest()

#         self._callFUT(request, statuses)

#         # キャンセルが呼ばれたかチェック
#         mock_cancel.assert_called_with()

#         # コミット回数をチェック
#         mock_session.commit.assert_called_with()

class Testget_auth_orders(unittest.TestCase):

    def setUp(self):
        _setup_db(modules=[
            "altair.multicheckout.models",
            ])

    def tearDown(self):
        _teardown_db()

    def _callFUT(self, *args, **kwargs):
        from .cancelauth import get_auth_orders
        return get_auth_orders(*args, **kwargs)

    def test_empty(self):
        request = testing.DummyRequest()
        shop_id = u"testing"

        result = self._callFUT(request, shop_id)

        self.assertEqual(result, [])

    def test_authorized(self):
        import altair.multicheckout.models as m
        s = m.MultiCheckoutOrderStatus(
            Storecd=u"testing",
            Status=unicode(m.MultiCheckoutStatusEnum.Authorized),
            updated_at=datetime(1970, 1, 1, 0, 0, 0))
        m._session.add(s)
        request = testing.DummyRequest()
        shop_id = u"testing"

        result = self._callFUT(request, shop_id)

        self.assertEqual(result, [s])

    def test_none_status(self):
        import altair.multicheckout.models as m
        s = m.MultiCheckoutOrderStatus(
            Storecd=u"testing",
            Status=None,
            updated_at=datetime(1970, 1, 1, 0, 0, 0))
        m._session.add(s)
        request = testing.DummyRequest()
        shop_id = u"testing"

        result = self._callFUT(request, shop_id)

        self.assertEqual(result, [s])
