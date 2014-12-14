# -*- coding:utf-8 -*-
from datetime import datetime, timedelta
import unittest
import mock
from pyramid import testing
from altair.multicheckout.interfaces import (
    IMulticheckoutSettingListFactory,
    IMulticheckoutImplFactory,
    )
from altair.app.ticketing.testing import _setup_db, _teardown_db

class TestCanceller(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db(modules=[
            "altair.multicheckout.models",
            "altair.app.ticketing.core.models",
            "altair.app.ticketing.orders.models",
            "altair.app.ticketing.cart.models",
            ])
        from altair.multicheckout.models import _session
        _session.remove()
        _session.configure(bind=self.session.bind)
        self.config = testing.setUp()

    def tearDown(self):
        from altair.multicheckout.api import remove_default_session
        remove_default_session()
        _teardown_db()
        testing.tearDown()

    def _getTarget(self):
        from .cancelauth import Canceller
        return Canceller

    def _makeOne(self, now=None, auth_cancel_expiry=None):
        return self._getTarget()(testing.DummyRequest(), now=now, auth_cancel_expiry=auth_cancel_expiry)

    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.Canceller.is_auth_cancelable')
    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.m')
    def test_cancel_auth_not_cancelable(self, mock_models, mock_cancelable):
        status = {
            'order_no': "testing-order",
            'is_authorized': True,
            'status': "110",
            'keep_auth_for': None
            }
        mock_cancelable.return_value = False
        target = self._makeOne()
        mock_api = mock.Mock()
        target.cancel_auth(mock_api, status)
        mock_cancelable.assert_called_with(status)
        self.assertFalse(mock_api.return_value.checkout_auth_cancel.called)
        self.assertFalse(mock_models._session.commit.called)

    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.Canceller.is_auth_cancelable')
    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.m')
    def test_cancel_auth_with_cancelable(self, mock_models, mock_cancelable):
        status = testing.DummyModel(OrderNo="testing-order", is_authorized=True, Status="100")
        status = {
            'order_no': "testing-order",
            'is_authorized': True,
            'status': "110",
            'keep_auth_for': None
            }
        mock_cancelable.return_value = True
        target = self._makeOne()
        mock_api = mock.Mock()
        target.cancel_auth(mock_api, status)
        mock_cancelable.assert_called_with(status)
        mock_api.checkout_auth_cancel.assert_called_with('testing-order')
        mock_models._session.commit.assert_called_with()

    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.Canceller.is_auth_cancelable')
    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.m')
    def test_cancel_auth_not_cancelable(self, mock_models, mock_cancelable):
        status = {
            'order_no': "testing-order",
            'is_authorized': True,
            'status': "120",
            'keep_auth_for': None,
            'sales_amount': 1000,
            'eventual_sales_amount': 500,
            'tax_carriage_amount_to_cancel': 0,
            }
        mock_cancelable.return_value = False
        target = self._makeOne()
        mock_api = mock.Mock()
        target.cancel_sales(mock_api, status)
        mock_api.checkout_sales_part_cancel.assert_called_with("testing-order", 500, 0)
        self.assertTrue(mock_models._session.commit.called)

    def test_is_auth_cancelable_no_keep_auth_for_with_valid_status(self):
        status = {
            'order_no': "testing-order",
            'is_authorized': True,
            'status': "100",
            'keep_auth_for': None
            }
        target = self._makeOne()
        result = target.is_auth_cancelable(status)
        self.assertTrue(result)

    def test_is_auth_cancelable_keep_auth_for_with_valid_status(self):
        status = {
            'order_no': "testing-order",
            'is_authorized': True,
            'status': "100",
            'keep_auth_for': 'lots'
            }
        target = self._makeOne()
        result = target.is_auth_cancelable(status)
        self.assertFalse(result)

    def test_get_auth_orders_empty(self):
        dummy_multicheckout_setting = testing.DummyModel(
            shop_name=u"testing",
            shop_id=u"00000"
            )
        target = self._makeOne()
        result = target.get_auth_orders(dummy_multicheckout_setting)
        self.assertEqual(result, [])

    def test_get_auth_orders_too_new(self):
        import altair.multicheckout.models as m
        s = m.MultiCheckoutOrderStatus(
            OrderNo=u"testing",
            Storecd=u"00000",
            Status=unicode(m.MultiCheckoutStatusEnum.Authorized),
            updated_at=datetime(2014, 1, 1, 0, 0, 0))
        m._session.add(s)
        dummy_multicheckout_setting = testing.DummyModel(
            shop_name=u"testing",
            shop_id=u"00000"
            )
        target = self._makeOne(now=datetime(2014, 1, 1, 0, 59, 59), auth_cancel_expiry=timedelta(hours=1))
        result = target.get_auth_orders(dummy_multicheckout_setting)
        self.assertEqual(result, [])

        target = self._makeOne(now=datetime(2014, 1, 1, 1, 0, 0), auth_cancel_expiry=timedelta(hours=1))
        result = target.get_auth_orders(dummy_multicheckout_setting)
        self.assertEqual(result, [])

        target = self._makeOne(now=datetime(2014, 1, 1, 1, 0, 1), auth_cancel_expiry=timedelta(hours=1))
        result = target.get_auth_orders(dummy_multicheckout_setting)
        self.assertEqual(result, [{
            'id': 1,
            'order_no': "testing",
            "keep_auth_for": None,
            'is_authorized': True,
            'status': s.Status,
            'sales_amount': s.SalesAmount,
            'eventual_sales_amount': None,
            'tax_carriage_amount_to_cancel': None,
            }])

    def test_get_auth_orders_authorized(self):
        import altair.multicheckout.models as m
        s = m.MultiCheckoutOrderStatus(
            OrderNo=u"testing",
            Storecd=u"00000",
            Status=unicode(m.MultiCheckoutStatusEnum.Authorized),
            updated_at=datetime(1970, 1, 1, 0, 0, 0))
        m._session.add(s)
        dummy_multicheckout_setting = testing.DummyModel(
            shop_name=u"testing",
            shop_id=u"00000"
            )
        target = self._makeOne()
        result = target.get_auth_orders(dummy_multicheckout_setting)
        self.assertEqual(result, [{
            'id': 1,
            'order_no': "testing",
            "keep_auth_for": None,
            'is_authorized': True,
            'status': s.Status,
            'sales_amount': s.SalesAmount,
            'eventual_sales_amount': None,
            'tax_carriage_amount_to_cancel': None,
            }])

    def test_get_auth_orders_none_status(self):
        import altair.multicheckout.models as m
        s = m.MultiCheckoutOrderStatus(
            Storecd=u"00000",
            OrderNo="testing",
            Status=None,
            updated_at=datetime(1970, 1, 1, 0, 0, 0)
            )
        m._session.add(s)
        dummy_multicheckout_setting = testing.DummyModel(
            shop_name=u"testing",
            shop_id=u"00000"
            )
        target = self._makeOne()
        result = target.get_auth_orders(dummy_multicheckout_setting)
        self.assertEqual(result, [{
            'id': 1,
            'order_no': "testing",
            "keep_auth_for": None,
            'is_authorized': False,
            'status': s.Status,
            'sales_amount': s.SalesAmount,
            'eventual_sales_amount': None,
            'tax_carriage_amount_to_cancel': None,
            }])

    def test_get_orders_to_be_canceled_empty(self):
        dummy_multicheckout_setting = testing.DummyModel(
            shop_name=u"testing",
            shop_id=u"00000"
            )
        target = self._makeOne()
        result = target.get_orders_to_be_canceled(dummy_multicheckout_setting)
        self.assertEqual(result, [])

    def test_get_orders_to_be_canceled_unscheduled(self):
        import altair.multicheckout.models as m
        s = m.MultiCheckoutOrderStatus(
            OrderNo=u"testing",
            Storecd=u"00000",
            Status=unicode(m.MultiCheckoutStatusEnum.Settled),
            CancellationScheduledAt=None,
            SalesAmount=100,
            EventualSalesAmount=50,
            TaxCarriageAmountToCancel=0, 
            updated_at=datetime(1970, 1, 1, 0, 0, 0)
            )
        m._session.add(s)
        dummy_multicheckout_setting = testing.DummyModel(
            shop_name=u"testing",
            shop_id=u"00000"
            )
        target = self._makeOne(now=datetime(2014, 1, 1, 0, 0, 0))
        result = target.get_orders_to_be_canceled(dummy_multicheckout_setting)
        self.assertEqual(result, [])

        target = self._makeOne(now=datetime(2014, 1, 1, 1, 0, 0))
        result = target.get_orders_to_be_canceled(dummy_multicheckout_setting)
        self.assertEqual(result, [])

    def test_get_orders_to_be_canceled_settled(self):
        import altair.multicheckout.models as m
        s = m.MultiCheckoutOrderStatus(
            OrderNo=u"testing",
            Storecd=u"00000",
            Status=unicode(m.MultiCheckoutStatusEnum.Settled),
            CancellationScheduledAt=datetime(2014, 1, 1, 1, 0, 0),
            SalesAmount=100,
            EventualSalesAmount=50,
            TaxCarriageAmountToCancel=0, 
            updated_at=datetime(1970, 1, 1, 0, 0, 0)
            )
        m._session.add(s)
        dummy_multicheckout_setting = testing.DummyModel(
            shop_name=u"testing",
            shop_id=u"00000"
            )
        target = self._makeOne(now=datetime(2014, 1, 1, 0, 0, 0))
        result = target.get_orders_to_be_canceled(dummy_multicheckout_setting)
        self.assertEqual(result, [])

        target = self._makeOne(now=datetime(2014, 1, 1, 1, 0, 0))
        result = target.get_orders_to_be_canceled(dummy_multicheckout_setting)
        self.assertEqual(result, [{
            'id': 1,
            'order_no': "testing",
            "keep_auth_for": None,
            'is_authorized': False,
            'status': s.Status,
            'sales_amount': s.SalesAmount,
            'eventual_sales_amount': s.EventualSalesAmount,
            'tax_carriage_amount_to_cancel': s.TaxCarriageAmountToCancel,
            }])

    def test_get_orders_to_be_canceled_part_canceled(self):
        import altair.multicheckout.models as m
        s = m.MultiCheckoutOrderStatus(
            OrderNo=u"testing",
            Storecd=u"00000",
            Status=unicode(m.MultiCheckoutStatusEnum.PartCanceled),
            CancellationScheduledAt=datetime(2014, 1, 1, 1, 0, 0),
            SalesAmount=100,
            updated_at=datetime(1970, 1, 1, 0, 0, 0))
        m._session.add(s)
        dummy_multicheckout_setting = testing.DummyModel(
            shop_name=u"testing",
            shop_id=u"00000"
            )
        target = self._makeOne(now=datetime(2014, 1, 1, 0, 0, 0))
        result = target.get_orders_to_be_canceled(dummy_multicheckout_setting)
        self.assertEqual(result, [])

        target = self._makeOne(now=datetime(2014, 1, 1, 1, 0, 0))
        result = target.get_orders_to_be_canceled(dummy_multicheckout_setting)
        self.assertEqual(result, [{
            'id': 1,
            'order_no': "testing",
            "keep_auth_for": None,
            'is_authorized': False,
            'status': s.Status,
            'sales_amount': s.SalesAmount,
            'eventual_sales_amount': s.EventualSalesAmount,
            'tax_carriage_amount_to_cancel': s.TaxCarriageAmountToCancel,
            }])

    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.m')
    def test_sync_data_one_authorized(self, mock_models):
        import altair.multicheckout.models as m
        status = {
            'order_no': "testing-order",
            'status': unicode(m.MultiCheckoutStatusEnum.Authorized),
            'keep_auth_for': None
            }
        target = self._makeOne()
        mock_api = mock.Mock()
        mock_api.checkout_inquiry.return_value = testing.DummyResource(
            Status='110',
            CmnErrorCd="000000",
        )
        result = target.sync_data(mock_api, status)
        mock_models._session.commit.assert_called_once()
        mock_api.checkout_inquiry.assert_called_with("testing-order", u"cancel auth batch")

    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.m')
    def test_sync_data_one_unknown(self, mock_models):
        import altair.multicheckout.models as m
        status = {
            'order_no': "testing-order",
            'status': None,
            'keep_auth_for': None,
            }
        target = self._makeOne()
        mock_api = mock.Mock()
        mock_api.checkout_inquiry.return_value = testing.DummyResource(
            Status='110', OrderNo="testing-order", Storecd="test-shop",
            CmnErrorCd="000000",
        )
        result = target.sync_data(mock_api, status)
        mock_models._session.commit.assert_called_once()
        mock_api.checkout_inquiry.assert_called_with("testing-order", u"cancel auth batch")

    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.m')
    def test_sync_data_one_invalid_order(self, mock_models):
        import altair.multicheckout.models as m
        status = {
            'order_no': "testing-order",
            'status': None,
            'keep_auth_for': None,
            }
        target = self._makeOne()
        mock_api = mock.Mock()
        mock_api.checkout_inquiry.return_value = testing.DummyResource(
            Status='110', OrderNo="testing-order", Storecd="test-shop",
            CmnErrorCd="001407",
        )
        result = target.sync_data(mock_api, status)
        mock_models._session.commit.assert_called_once()
        mock_api.checkout_inquiry.assert_called_with("testing-order", u"cancel auth batch")

    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.m')
    def test_sync_data_one_bad_response(self, mock_models):
        import altair.multicheckout.models as m
        status = {
            'order_no': "testing-order",
            'status': None,
            'keep_auth_for': None,
            }
        target = self._makeOne()
        mock_api = mock.Mock()
        mock_api.checkout_inquiry.return_value = testing.DummyResource(
            Status='110', OrderNo="testing-order", Storecd="test-shop",
            CmnErrorCd="999999",
        )
        result = target.sync_data(mock_api, status)
        mock_models._session.commit.assert_called_once()
        mock_api.checkout_inquiry.assert_called_with("testing-order", u"cancel auth batch")

    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.m')
    def test_sync_data_one_keep_and_valid_status(self, mock_models):
        import altair.multicheckout.models as m
        status = {
            'order_no': "testing-order",
            'status': unicode(m.MultiCheckoutStatusEnum.Authorized),
            'keep_auth_for': 'lots',
            }
        target = self._makeOne()
        mock_api = mock.Mock()
        mock_api.checkout_inquiry.return_value = testing.DummyResource(
            Status='110', OrderNo="testing-order", Storecd="test-shop",
            CmnErrorCd="000000",
        )
        result = target.sync_data(mock_api, status)
        mock_models._session.commit.assert_called_once()
        self.assertTrue(mock_api.checkout_inquiry.called)

    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.m')
    def test_sync_data_one_keep_and_invalid_status(self, mock_models):
        import altair.multicheckout.models as m
        status = {
            'order_no': "testing-order",
            'status': None,
            'keep_auth_for': 'lots',
            }
        target = self._makeOne()
        mock_api = mock.Mock()
        mock_api.checkout_inquiry.return_value = testing.DummyResource(
            Status='110', OrderNo="testing-order", Storecd="test-shop",
            CmnErrorCd="000000",
        )
        result = target.sync_data(mock_api, status)
        mock_models._session.commit.assert_called_once()
        mock_api.checkout_inquiry.assert_called_with("testing-order", u"cancel auth batch")

    def test_run_empty_shops(self):
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
        target = self._makeOne()
        result = target.run()
        self.assertEqual(result, [])

    @mock.patch('altair.app.ticketing.multicheckout.scripts.cancelauth.Canceller.process_shop')
    def test_run_one_shops(self, mock_process_shop):
        multicheckout_setting_0 = testing.DummyModel(
            shop_name='testing-shop',
            shop_id="testing"
            )
        self.config.registry.utilities.register(
            [],
            IMulticheckoutSettingListFactory,
            "",
            lambda request: [multicheckout_setting_0]
            )
        target = self._makeOne()
        result = target.run()
        mock_process_shop.assert_called_with(multicheckout_setting_0)
