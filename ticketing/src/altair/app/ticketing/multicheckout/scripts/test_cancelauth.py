# -*- coding:utf-8 -*-
from datetime import datetime
import unittest
import mock
from pyramid import testing
from altair.multicheckout.interfaces import (
    IMulticheckoutSettingListFactory,
    IMulticheckoutImplFactory,
    )
from altair.app.ticketing.testing import _setup_db, _teardown_db

class Testcancel_auth(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from . cancelauth import cancel_auth
        return cancel_auth(*args, **kwargs)

    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.get_multicheckout_3d_api')
    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.m')
    def test_empty(self, mock_models, mock_api):
        statuses = []
        request = testing.DummyRequest()

        self._callFUT(request, statuses, 'shop_name')

        self.assertFalse(mock_api.return_value.checkout_auth_cancel.called)
        self.assertFalse(mock_models._session.commit.called)

    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.is_cancelable')
    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.get_multicheckout_3d_api')
    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.m')
    def test_not_cancelable(self, mock_models, mock_api, mock_cancelable):
        statuses = [testing.DummyModel(OrderNo="testing-order")]
        mock_cancelable.return_value = False
        request = testing.DummyRequest()

        self._callFUT(request, statuses, 'shop_name')

        mock_cancelable.assert_called_with(request, statuses[0])
        self.assertFalse(mock_api.return_value.checkout_auth_cancel.called)
        self.assertFalse(mock_models._session.commit.called)

    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.is_cancelable')
    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.get_multicheckout_3d_api')
    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.m')
    def test_with_cancelable_without_authorized(self, mock_models, mock_api, mock_cancelable):
        statuses = [testing.DummyModel(OrderNo="testing-order",
                                       is_authorized=False,
                                       Status="100")]
        mock_cancelable.return_value = True
        request = testing.DummyRequest()

        self._callFUT(request, statuses, 'shop_name')

        mock_cancelable.assert_called_with(request, statuses[0])
        self.assertFalse(mock_api.checkout_auth_cancel.called)
        self.assertFalse(mock_models._session.commit.called)

    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.is_cancelable')
    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.get_multicheckout_3d_api')
    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.m')
    def test_with_cancelable_with_authorized(self, mock_models, mock_api, mock_cancelable):
        statuses = [testing.DummyModel(OrderNo="testing-order",
                                       is_authorized=True,
                                       Status="100")]
        mock_cancelable.return_value = True
        request = testing.DummyRequest()

        self._callFUT(request, statuses, 'shop_name')

        mock_cancelable.assert_called_with(request, statuses[0])
        mock_api.return_value.checkout_auth_cancel.assert_called_with('testing-order')
        mock_models._session.commit.assert_called_with()


class Testis_cancelable(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from . cancelauth import is_cancelable
        return is_cancelable(*args, **kwargs)

    def test_no_keep_auth_for_with_valid_status(self):
        status = testing.DummyModel(OrderNo="testing-order",
                                    is_authorized=True,
                                    Status="100",
                                    KeepAuthFor=None)
        request = testing.DummyRequest()

        result = self._callFUT(request, status)

        self.assertTrue(result)

    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.get_cancel_filter')
    def test_keep_auth_for_with_valid_status(self, mock_api):
        status = testing.DummyModel(OrderNo="testing-order",
                                    is_authorized=True,
                                    Status="100",
                                    KeepAuthFor='lots')
        mock_instance = mock_api.return_value
        mock_instance.is_cancelable.return_value = False
        request = testing.DummyRequest()

        result = self._callFUT(request, status)

        self.assertFalse(result)


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

    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.get_multicheckout_3d_api')
    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.m')
    def test_empty(self, mock_models, mock_api):
        request = testing.DummyRequest()
        statuses = []

        self._callFUT(request, statuses, 'shop_name')

        self.assertFalse(mock_models._session.commit.called)

    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.get_multicheckout_3d_api')
    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.m')
    def test_one_authorized_actualy_authorized(self, mock_models, mock_api):
        import altair.multicheckout.models as m
        mock_api.return_value.checkout_inquiry.return_value = testing.DummyResource(
            Status='110',
            CmnErrorCd="000000",
        )
        request = testing.DummyRequest()
        statuses = [
            testing.DummyModel(
                OrderNo="testing-order",
                Status=unicode(m.MultiCheckoutStatusEnum.Authorized),
                KeepAuthFor=None
            )]

        self._callFUT(request, statuses, 'shop_name')
        mock_models._session.commit.assert_called_once()
        mock_api.return_value.checkout_inquiry.assert_called_with("testing-order", u"cancel auth batch")

    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.get_multicheckout_3d_api')
    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.m')
    def test_one_unknown_actualy_authorized(self, mock_models, mock_api):
        import altair.multicheckout.models as m
        mock_api.return_value.checkout_inquiry.return_value = testing.DummyResource(
            Status='110', OrderNo="testing-order", Storecd="test-shop",
            CmnErrorCd="000000",
        )
        request = testing.DummyRequest()
        statuses = [
            testing.DummyModel(
                OrderNo="testing-order",
                Status=None,
                KeepAuthFor=None
            )]

        self._callFUT(request, statuses, 'shop_name')
        mock_models._session.commit.assert_called_once()
        mock_api.return_value.checkout_inquiry.assert_called_with("testing-order", u"cancel auth batch")

    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.get_multicheckout_3d_api')
    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.m')
    def test_one_invalid_order(self, mock_models, mock_api):
        mock_api.return_value.checkout_inquiry.return_value = testing.DummyResource(
            Status='110', OrderNo="testing-order", Storecd="test-shop",
            CmnErrorCd="001407",
        )
        request = testing.DummyRequest()
        statuses = [
            testing.DummyModel(
                OrderNo="testing-order",
                Status=None,
                KeepAuthFor=None
            )]

        self._callFUT(request, statuses, 'shop_name')
        mock_models._session.commit.assert_called_once()
        mock_api.return_value.checkout_inquiry.assert_called_with("testing-order", u"cancel auth batch")

    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.get_multicheckout_3d_api')
    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.m')
    def test_one_bad_response(self, mock_models, mock_api):
        mock_api.return_value.checkout_inquiry.return_value = testing.DummyResource(
            Status='110', OrderNo="testing-order", Storecd="test-shop",
            CmnErrorCd="999999",
        )
        request = testing.DummyRequest()
        statuses = [
            testing.DummyModel(
                OrderNo="testing-order",
                Status=None,
                KeepAuthFor=None
            )]

        self._callFUT(request, statuses, 'shop_name')
        mock_models._session.commit.assert_called_once()
        mock_api.return_value.checkout_inquiry.assert_called_with("testing-order", u"cancel auth batch")

    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.get_multicheckout_3d_api')
    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.m')
    def test_one_keep_and_valid_status(self, mock_models, mock_api):
        import altair.multicheckout.models as m
        mock_api.return_value.checkout_inquiry.return_value = testing.DummyResource(
            Status='110', OrderNo="testing-order", Storecd="test-shop",
            CmnErrorCd="000000",
        )
        request = testing.DummyRequest()
        statuses = [
            testing.DummyModel(
                OrderNo="testing-order",
                Status=unicode(m.MultiCheckoutStatusEnum.Authorized),
                KeepAuthFor='lots'
            )]

        self._callFUT(request, statuses, 'shop_name')
        mock_models._session.commit.assert_called_once()
        self.assertFalse(mock_api.return_value.checkout_inquiry.called)

    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.get_multicheckout_3d_api')
    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.m')
    def test_one_keep_and_invalid_status(self, mock_models, mock_api):
        mock_api.return_value.checkout_inquiry.return_value = testing.DummyResource(
            Status='110', OrderNo="testing-order", Storecd="test-shop",
            CmnErrorCd="000000",
        )
        request = testing.DummyRequest()
        statuses = [
            testing.DummyModel(
                OrderNo="testing-order",
                Status=None,
                KeepAuthFor='lots'
            )]

        self._callFUT(request, statuses, 'shop_name')
        mock_models._session.commit.assert_called_once()
        mock_api.return_value.checkout_inquiry.assert_called_with("testing-order", u"cancel auth batch")


class Testrun(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from .cancelauth import run
        return run(*args, **kwargs)

    def test_empty_shops(self):
        self.config.registry.utilities.register(
            [],
            IMulticheckoutSettingListFactory,
            "",
            lambda request: [],
        )
        self.multicheckout_impl = mock.Mock()
        self.config.registry.utilities.register(
            [],
            IMulticheckoutImplFactory,
            "",
            lambda request, override_name: self.multicheckout_impl
        )
        request = testing.DummyRequest()
        result = self._callFUT(request)

        self.assertEqual(result, [])

    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.process_shop')
    def test_one_shops(self, mock_process_shop):
        self.config.registry.utilities.register(
            [],
            IMulticheckoutSettingListFactory,
            "",
            lambda request: [testing.DummyModel(
                shop_name='testing-shop',
                shop_id="testing",
            )],
        )
        request = testing.DummyRequest()
        result = self._callFUT(request)

        mock_process_shop.assert_called_with(request, 'testing', 'testing-shop')
