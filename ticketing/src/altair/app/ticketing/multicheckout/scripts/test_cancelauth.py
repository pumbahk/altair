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


class Testsync_data(unittest.TestCase):

    def _callFUT(self, *args, **kwargs):
        from .cancelauth import sync_data
        return sync_data(*args, **kwargs)

    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.m')
    def test_empty(self, mock_models):
        request = testing.DummyRequest()
        statuses = []

        self._callFUT(request, statuses)

        self.assertFalse(mock_models._session.commit.called)

    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.api')
    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.m')
    def test_one_authorized_actualy_authorized(self, mock_models, mock_api):
        import altair.multicheckout.models as m
        mock_api.checkout_inquiry.return_value = testing.DummyResource(Status='110')
        request = testing.DummyRequest()
        statuses = [
            testing.DummyModel(
                OrderNo="testing-order",
                Status=unicode(m.MultiCheckoutStatusEnum.Authorized),
            )]

        self._callFUT(request, statuses)
        mock_models._session.commit.assert_called_once()
        self.assertFalse(mock_models.MultiCheckoutOrderStatus.set_status.called)

    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.api')
    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.m')
    def test_one_unknown_actualy_authorized(self, mock_models, mock_api):
        import altair.multicheckout.models as m
        mock_api.checkout_inquiry.return_value = testing.DummyResource(Status='110', OrderNo="testing-order", Storecd="test-shop")
        request = testing.DummyRequest()
        statuses = [
            testing.DummyModel(
                OrderNo="testing-order",
                Status=None,
            )]

        self._callFUT(request, statuses)
        mock_models._session.commit.assert_called_once()
        mock_api.checkout_inquiry.assert_called_with(
            request,
            "testing-order")
        mock_models.MultiCheckoutOrderStatus.set_status.assert_called_with(
            "testing-order",
            "test-shop",
            unicode(m.MultiCheckoutStatusEnum.Authorized),
            u"by cancel auth batch",
        )
