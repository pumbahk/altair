# -*- coding:utf-8 -*-

import unittest
import datetime
from altair.app.ticketing.testing import DummyRequest, _setup_db, _teardown_db
from altair.app.ticketing.core.testing import CoreTestMixin
from altair.app.ticketing.cart.testing import CartTestMixin
import mock
from pyramid.testing import DummyModel


class CompletionViewlet(unittest.TestCase):
    @staticmethod
    def _getTestTarget():
        from . import pgw_credit_card
        return pgw_credit_card.completion_viewlet

    def test_completion_viewlet(self):
        """ completion_viewletの正常系テスト """
        test_context = {}
        request = DummyRequest()

        complete_viewlet_dict = self._getTestTarget()(test_context, request)
        self.assertIsNotNone(complete_viewlet_dict)


class CompletionPaymentMailViewletTest(unittest.TestCase):
    @staticmethod
    def _getTestTarget():
        from . import pgw_credit_card
        return pgw_credit_card.completion_payment_mail_viewlet

    def test_completion_payment_mail_viewlet(self):
        """ completion_payment_mail_viewletの正常系テスト """
        test_context = {}
        request = DummyRequest()
        self._getTestTarget()(test_context, request)


class CancelPaymentMailViewletTest(unittest.TestCase):
    @staticmethod
    def _getTestTarget():
        from . import pgw_credit_card
        return pgw_credit_card.cancel_payment_mail_viewlet

    def test_cancel_payment_mail_viewlet(self):
        """ cancel_payment_mail_viewletの正常系テスト """
        test_context = {}
        request = DummyRequest()
        self._getTestTarget()(test_context, request)


class PaymentGatewayCreditCardPaymentPluginTest(unittest.TestCase, CoreTestMixin, CartTestMixin):
    def setUp(self):
        self.session = _setup_db([
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.orders.models',
            'altair.app.ticketing.cart.models',
        ])
        CoreTestMixin.setUp(self)

    def tearDown(self):
        self.session.remove()
        _teardown_db()

    @staticmethod
    def _getTestTarget():
        from . import pgw_credit_card
        return pgw_credit_card.PaymentGatewayCreditCardPaymentPlugin()

    def test_validate_order(self):
        """ validate_orderの正常系テスト """
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order_like = DummyModel(
            total_amount=100,
            payment_amount=100
        )
        plugin.validate_order(request, test_order_like)

    def test_validate_order_invalid_total_amount(self):
        """ validate_orderで総額が不正の場合のテスト """
        from altair.app.ticketing.payments.exceptions import OrderLikeValidationFailure
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order_like = DummyModel(
            total_amount=0,
            payment_amount=0
        )
        with self.assertRaises(OrderLikeValidationFailure):
            plugin.validate_order(request, test_order_like)

    def test_validate_order_invalid_payment_amount(self):
        """ validate_orderで支払額が不正の場合のテスト """
        from altair.app.ticketing.payments.exceptions import OrderLikeValidationFailure
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order_like = DummyModel(
            total_amount=100,
            payment_amount=-1
        )
        with self.assertRaises(OrderLikeValidationFailure):
            plugin.validate_order(request, test_order_like)

    def test_validate_order_cancellation(self):
        """ validate_order_cancellationの正常系テスト """
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order = {}
        now = datetime.datetime.now()
        plugin.validate_order_cancellation(request, test_order, now)

    def test_prepare(self):
        """ prepareの正常系テスト """
        from pyramid.httpexceptions import HTTPFound
        plugin = self._getTestTarget()

        def mock_route_url(arg1):
            return 'http://dummy_route_url'

        request = DummyRequest(
            session={},
            route_url=mock_route_url
        )
        test_auth_model = u'test_auth_model'
        test_cart = DummyModel(
            sales_segment=DummyModel(
                auth3d_notice=test_auth_model
            )
        )
        http_exception = plugin.prepare(request, test_cart)
        self.assertIsInstance(http_exception, HTTPFound)
        self.assertEqual(request.session['altair.app.ticketing.payments.auth3d_notice'], test_auth_model)

    def _create_base_test_cart(self):
        from altair.app.ticketing.core.models import SalesSegmentGroup, SalesSegment
        from altair.app.ticketing.cart.models import CartSetting
        from datetime import datetime
        # see CoreTestMixin and CartTestMixin
        test_stock_types = self._create_stock_types(1)
        test_stocks = self._create_stocks(test_stock_types)
        test_products = self._create_products(test_stocks)
        test_sales_segment_group = SalesSegmentGroup(event=self.event)
        test_sales_segment = SalesSegment(performance=self.performance, sales_segment_group=test_sales_segment_group)
        test_pdmp = self._create_payment_delivery_method_pairs(test_sales_segment_group)[0]
        test_cart_setting = CartSetting(type='standard')
        test_cart = self._create_cart(
            zip(test_products, [1]),
            test_sales_segment,
            test_cart_setting,
            pdmp=test_pdmp
        )
        test_cart.point_amount = 0
        test_cart.created_at = datetime.now()
        return test_cart

    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.authorize_and_capture')
    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.find_payment')
    def test_finish_success_with_initialized_status(self, find_payment, authorize_and_capture):
        """ finishの正常系テスト　決済処理成功_決済ステータス initialized """
        from altair.app.ticketing.core.models import OrganizationSetting
        from altair.app.ticketing.payments.plugins import dummy_pgw_api as api
        plugin = self._getTestTarget()

        request = DummyRequest()
        organization_setting = OrganizationSetting(
            organization_id=self.organization.id,
            pgw_sub_service_id=u'1234'
        )
        self.session.add(organization_setting)
        test_cart = self._create_base_test_cart()
        find_payment.return_value = {
            u'paymentStatusType': api.PGW_PAYMENT_STATUS_TYPE_INITIALIZED,
            u'grossAmount': 0
        }
        authorize_and_capture.return_value = {
            u'resultType': api.PGW_API_RESULT_TYPE_SUCCESS
        }

        order = plugin.finish(request, test_cart)
        self.assertIsNotNone(order)
        self.assertIsNotNone(order.paid_at)
        self.assertIsNotNone(test_cart.finished_at)

    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.authorize_and_capture')
    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.find_payment')
    def test_finish_failure_with_initialized_status(self, find_payment, authorize_and_capture):
        """ finishの準正常系テスト　決済処理失敗_決済ステータス initialized """
        from altair.app.ticketing.core.models import OrganizationSetting
        from altair.app.ticketing.payments.plugins import dummy_pgw_api as api
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure
        plugin = self._getTestTarget()

        request = DummyRequest()
        organization_setting = OrganizationSetting(
            organization_id=self.organization.id,
            pgw_sub_service_id=u'1234'
        )
        self.session.add(organization_setting)
        test_cart = self._create_base_test_cart()
        find_payment.return_value = {
            u'paymentStatusType': api.PGW_PAYMENT_STATUS_TYPE_INITIALIZED,
            u'grossAmount': 0
        }
        authorize_and_capture.return_value = {
            u'resultType': api.PGW_API_RESULT_TYPE_FAILURE
        }

        with self.assertRaises(PgwCardPaymentPluginFailure):
            plugin.finish(request, test_cart)

    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.authorize_and_capture')
    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.find_payment')
    def test_finish_pending_with_initialized_status(self, find_payment, authorize_and_capture):
        """
        finishの準正常系テスト　決済処理ペンディング_決済ステータス initialized
        ペンディングで決済失敗になることを確認(1パターンで確認できればよい)
        """
        from altair.app.ticketing.core.models import OrganizationSetting
        from altair.app.ticketing.payments.plugins import dummy_pgw_api as api
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure
        plugin = self._getTestTarget()

        request = DummyRequest()
        organization_setting = OrganizationSetting(
            organization_id=self.organization.id,
            pgw_sub_service_id=u'1234'
        )
        self.session.add(organization_setting)
        test_cart = self._create_base_test_cart()
        find_payment.return_value = {
            u'paymentStatusType': api.PGW_PAYMENT_STATUS_TYPE_INITIALIZED,
            u'grossAmount': 0
        }
        authorize_and_capture.return_value = {
            u'resultType': api.PGW_API_RESULT_TYPE_PENDING
        }

        with self.assertRaises(PgwCardPaymentPluginFailure):
            plugin.finish(request, test_cart)

    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.capture')
    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.find_payment')
    def test_finish_success_with_authorized_status(self, find_payment, capture):
        """ finishの正常系テスト　決済処理成功_決済ステータス authorized """
        from altair.app.ticketing.core.models import OrganizationSetting
        from altair.app.ticketing.payments.plugins import dummy_pgw_api as api
        plugin = self._getTestTarget()

        request = DummyRequest()
        organization_setting = OrganizationSetting(
            organization_id=self.organization.id,
            pgw_sub_service_id=u'1234'
        )
        self.session.add(organization_setting)
        test_cart = self._create_base_test_cart()
        find_payment.return_value = {
            u'paymentStatusType': api.PGW_PAYMENT_STATUS_TYPE_AUTHORIZED,
            u'grossAmount': test_cart.payment_amount
        }
        capture.return_value = {
            u'resultType': api.PGW_API_RESULT_TYPE_SUCCESS,
        }

        order = plugin.finish(request, test_cart)
        self.assertIsNotNone(order)
        self.assertIsNotNone(order.paid_at)
        self.assertIsNotNone(test_cart.finished_at)

    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.capture')
    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.find_payment')
    def test_finish_failure_with_authorized_status(self, find_payment, capture):
        """ finishの準正常系テスト　決済処理失敗_決済ステータス authorized """
        from altair.app.ticketing.core.models import OrganizationSetting
        from altair.app.ticketing.payments.plugins import dummy_pgw_api as api
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure
        plugin = self._getTestTarget()

        request = DummyRequest()
        organization_setting = OrganizationSetting(
            organization_id=self.organization.id,
            pgw_sub_service_id=u'1234'
        )
        self.session.add(organization_setting)
        test_cart = self._create_base_test_cart()
        find_payment.return_value = {
            u'paymentStatusType': api.PGW_PAYMENT_STATUS_TYPE_AUTHORIZED,
            u'grossAmount': test_cart.payment_amount
        }
        capture.return_value = {
            u'resultType': api.PGW_API_RESULT_TYPE_FAILURE
        }

        with self.assertRaises(PgwCardPaymentPluginFailure):
            plugin.finish(request, test_cart)

    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.capture')
    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.modify')
    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.find_payment')
    def test_finish_success_with_authorized_status_and_modify_amount(self, find_payment, modify, capture):
        """ finishの正常系テスト　決済処理成功_決済ステータス authorized オーソリ金額から減額あり """
        from altair.app.ticketing.core.models import OrganizationSetting
        from altair.app.ticketing.payments.plugins import dummy_pgw_api as api
        plugin = self._getTestTarget()

        request = DummyRequest()
        organization_setting = OrganizationSetting(
            organization_id=self.organization.id,
            pgw_sub_service_id=u'1234'
        )
        self.session.add(organization_setting)
        test_cart = self._create_base_test_cart()
        find_payment.return_value = {
            u'paymentStatusType': api.PGW_PAYMENT_STATUS_TYPE_AUTHORIZED,
            u'grossAmount': test_cart.payment_amount + 10
        }
        modify.return_value = {
            u'resultType': api.PGW_API_RESULT_TYPE_SUCCESS,
        }
        capture.return_value = {
            u'resultType': api.PGW_API_RESULT_TYPE_SUCCESS,
        }

        order = plugin.finish(request, test_cart)
        self.assertIsNotNone(order)
        self.assertIsNotNone(order.paid_at)
        self.assertIsNotNone(test_cart.finished_at)

    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.capture')
    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.modify')
    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.find_payment')
    def test_finish_failure_with_authorized_status_and_modify_amount(self, find_payment, modify, capture):
        """ finishの準正常系テスト　決済処理失敗_決済ステータス authorized オーソリ金額から減額あり """
        from altair.app.ticketing.core.models import OrganizationSetting
        from altair.app.ticketing.payments.plugins import dummy_pgw_api as api
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure
        plugin = self._getTestTarget()

        request = DummyRequest()
        organization_setting = OrganizationSetting(
            organization_id=self.organization.id,
            pgw_sub_service_id=u'1234'
        )
        self.session.add(organization_setting)
        test_cart = self._create_base_test_cart()
        find_payment.return_value = {
            u'paymentStatusType': api.PGW_PAYMENT_STATUS_TYPE_AUTHORIZED,
            u'grossAmount': test_cart.payment_amount + 10
        }
        modify.return_value = {
            u'resultType': api.PGW_API_RESULT_TYPE_FAILURE,
        }

        with self.assertRaises(PgwCardPaymentPluginFailure):
            plugin.finish(request, test_cart)
        self.assertFalse(capture.called)

    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.modify')
    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.find_payment')
    def test_finish_success_with_captured_status_and_modify_amount(self, find_payment, modify):
        """ finishの正常系テスト　決済処理成功_決済ステータス captured 確定金額から減額あり """
        from altair.app.ticketing.core.models import OrganizationSetting
        from altair.app.ticketing.payments.plugins import dummy_pgw_api as api
        plugin = self._getTestTarget()

        request = DummyRequest()
        organization_setting = OrganizationSetting(
            organization_id=self.organization.id,
            pgw_sub_service_id=u'1234'
        )
        self.session.add(organization_setting)
        test_cart = self._create_base_test_cart()
        find_payment.return_value = {
            u'paymentStatusType': api.PGW_PAYMENT_STATUS_TYPE_CAPTURED,
            u'grossAmount': test_cart.payment_amount + 10
        }
        modify.return_value = {
            u'resultType': api.PGW_API_RESULT_TYPE_SUCCESS,
        }

        order = plugin.finish(request, test_cart)
        self.assertIsNotNone(order)
        self.assertIsNotNone(order.paid_at)
        self.assertIsNotNone(test_cart.finished_at)

    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.modify')
    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.find_payment')
    def test_finish_failure_with_captured_status_and_modify_amount(self, find_payment, modify):
        """ finishの準正常系テスト　決済処理失敗_決済ステータス captured オーソリ金額から減額あり """
        from altair.app.ticketing.core.models import OrganizationSetting
        from altair.app.ticketing.payments.plugins import dummy_pgw_api as api
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure
        plugin = self._getTestTarget()

        request = DummyRequest()
        organization_setting = OrganizationSetting(
            organization_id=self.organization.id,
            pgw_sub_service_id=u'1234'
        )
        self.session.add(organization_setting)
        test_cart = self._create_base_test_cart()
        find_payment.return_value = {
            u'paymentStatusType': api.PGW_PAYMENT_STATUS_TYPE_CAPTURED,
            u'grossAmount': test_cart.payment_amount + 10
        }
        modify.return_value = {
            u'resultType': api.PGW_API_RESULT_TYPE_FAILURE,
        }

        with self.assertRaises(PgwCardPaymentPluginFailure):
            plugin.finish(request, test_cart)

    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.modify')
    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.find_payment')
    def test_finish_success_with_captured_status_and_same_amount(self, find_payment, modify):
        """ finishの正常系テスト　決済処理成功_決済ステータス captured 確定金額から減額あり """
        from altair.app.ticketing.core.models import OrganizationSetting
        from altair.app.ticketing.payments.plugins import dummy_pgw_api as api
        plugin = self._getTestTarget()

        request = DummyRequest()
        organization_setting = OrganizationSetting(
            organization_id=self.organization.id,
            pgw_sub_service_id=u'1234'
        )
        self.session.add(organization_setting)
        test_cart = self._create_base_test_cart()
        find_payment.return_value = {
            u'paymentStatusType': api.PGW_PAYMENT_STATUS_TYPE_CAPTURED,
            u'grossAmount': test_cart.payment_amount
        }

        order = plugin.finish(request, test_cart)
        self.assertIsNotNone(order)
        self.assertIsNotNone(order.paid_at)
        self.assertIsNotNone(test_cart.finished_at)
        self.assertFalse(modify.called)

    def test_finish_point_all_use(self):
        """ finishの正常系テスト 全額ポイント払いのため決済スキップ """
        from altair.app.ticketing.core.models import OrganizationSetting
        plugin = self._getTestTarget()

        request = DummyRequest()
        organization_setting = OrganizationSetting(
            organization_id=self.organization.id,
            pgw_sub_service_id=u'1234'
        )
        self.session.add(organization_setting)
        test_cart = self._create_base_test_cart()
        test_cart.point_amount = test_cart.total_amount

        order = plugin.finish(request, test_cart)
        self.assertIsNotNone(order)
        self.assertIsNotNone(order.paid_at)
        self.assertIsNotNone(test_cart.finished_at)

    def test_finish_no_sub_service_id(self):
        """ finishの異常系テスト Org設定にpgw_sub_service_idなし """
        from altair.app.ticketing.core.models import OrganizationSetting
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure
        plugin = self._getTestTarget()

        request = DummyRequest()
        organization_setting = OrganizationSetting(
            organization_id=self.organization.id,
        )
        self.session.add(organization_setting)
        test_cart = self._create_base_test_cart()

        with self.assertRaises(PgwCardPaymentPluginFailure):
            plugin.finish(request, test_cart)

    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.find_payment')
    def test_finish_invalid_payment_status_type(self, find_payment):
        """ finishの異常系テスト 決済ステータスが不正 """
        from altair.app.ticketing.core.models import OrganizationSetting
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure
        plugin = self._getTestTarget()

        request = DummyRequest()
        organization_setting = OrganizationSetting(
            organization_id=self.organization.id,
            pgw_sub_service_id=u'1234'
        )
        self.session.add(organization_setting)
        test_cart = self._create_base_test_cart()
        find_payment.return_value = {
            u'paymentStatusType': u'canceled',
            u'grossAmount': 0
        }

        with self.assertRaises(PgwCardPaymentPluginFailure):
            plugin.finish(request, test_cart)

    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.find_payment')
    def test_finish_invalid_amount(self, find_payment):
        """ finishの異常系テスト 決済額を増額に変更 """
        from altair.app.ticketing.core.models import OrganizationSetting
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure
        from altair.app.ticketing.payments.plugins import dummy_pgw_api as api
        plugin = self._getTestTarget()

        request = DummyRequest()
        organization_setting = OrganizationSetting(
            organization_id=self.organization.id,
            pgw_sub_service_id=u'1234'
        )
        self.session.add(organization_setting)
        test_cart = self._create_base_test_cart()
        find_payment.return_value = {
            u'paymentStatusType': api.PGW_PAYMENT_STATUS_TYPE_AUTHORIZED,
            u'grossAmount': test_cart.payment_amount - 10
        }

        with self.assertRaises(PgwCardPaymentPluginFailure):
            plugin.finish(request, test_cart)

    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.find_payment')
    def test_finish_unexpected_error(self, find_payment):
        """ finishの異常系テスト 予期せぬ例外発生 """
        from altair.app.ticketing.core.models import OrganizationSetting
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure
        plugin = self._getTestTarget()

        request = DummyRequest()
        organization_setting = OrganizationSetting(
            organization_id=self.organization.id,
            pgw_sub_service_id=u'1234'
        )
        self.session.add(organization_setting)
        test_cart = self._create_base_test_cart()
        find_payment.side_effect = ValueError

        with self.assertRaises(PgwCardPaymentPluginFailure):
            plugin.finish(request, test_cart)

    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.authorize_and_capture')
    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.find_payment')
    def test_finish2(self, find_payment, authorize_and_capture):
        """ finish2の正常系テスト(大部分をfinishのテストで確認済みのため、正常系を1パターンのみ確認) """
        from altair.app.ticketing.core.models import OrganizationSetting
        from altair.app.ticketing.payments.plugins import dummy_pgw_api as api
        plugin = self._getTestTarget()

        request = DummyRequest()
        organization_setting = OrganizationSetting(
            organization_id=self.organization.id,
            pgw_sub_service_id=u'1234'
        )
        self.session.add(organization_setting)
        test_cart = self._create_base_test_cart()
        find_payment.return_value = {
            u'paymentStatusType': api.PGW_PAYMENT_STATUS_TYPE_INITIALIZED,
            u'grossAmount': 0
        }
        authorize_and_capture.return_value = {
            u'resultType': api.PGW_API_RESULT_TYPE_SUCCESS
        }

        plugin.finish2(request, test_cart)
        self.assertTrue(find_payment.called)
        self.assertTrue(authorize_and_capture.called)

    def test_sales(self):
        """ salesの正常系テスト """
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_cart = {}
        plugin.sales(request, test_cart)

    def test_finished(self):
        """ finishedの正常系テスト """
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order = {}
        plugin.finished(request, test_order)

    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.cancel')
    def test_cancel_success(self, cancel):
        """ cancelの正常系テスト キャンセル成功 """
        from altair.app.ticketing.core.models import OrganizationSetting, PointUseTypeEnum
        from altair.app.ticketing.payments.plugins import dummy_pgw_api as api
        plugin = self._getTestTarget()

        request = DummyRequest()
        organization_setting = OrganizationSetting(
            organization_id=self.organization.id,
            pgw_sub_service_id=u'1234'
        )
        self.session.add(organization_setting)
        test_order = DummyModel(
            organization_id=self.organization.id,
            order_no=u'TEST000001',
            point_use_type=PointUseTypeEnum.NoUse
        )
        now = datetime.datetime.now()
        cancel.return_value = {
            u'resultType': api.PGW_API_RESULT_TYPE_SUCCESS
        }

        plugin.cancel(request, test_order, now)
        self.assertTrue(cancel.called)

    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.cancel')
    def test_cancel_failure(self, cancel):
        """ cancelの準正常系テスト キャンセル失敗 """
        from altair.app.ticketing.core.models import OrganizationSetting, PointUseTypeEnum
        from altair.app.ticketing.payments.plugins import dummy_pgw_api as api
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure
        plugin = self._getTestTarget()

        request = DummyRequest()
        organization_setting = OrganizationSetting(
            organization_id=self.organization.id,
            pgw_sub_service_id=u'1234'
        )
        self.session.add(organization_setting)
        test_order = DummyModel(
            organization_id=self.organization.id,
            order_no=u'TEST000001',
            point_use_type=PointUseTypeEnum.NoUse
        )
        now = datetime.datetime.now()
        cancel.return_value = {
            u'resultType': api.PGW_API_RESULT_TYPE_FAILURE
        }

        with self.assertRaises(PgwCardPaymentPluginFailure):
            plugin.cancel(request, test_order, now)

    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.cancel')
    def test_cancel_pending(self, cancel):
        """ cancelの準正常系テスト キャンセルPending """
        from altair.app.ticketing.core.models import OrganizationSetting, PointUseTypeEnum
        from altair.app.ticketing.payments.plugins import dummy_pgw_api as api
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure
        plugin = self._getTestTarget()

        request = DummyRequest()
        organization_setting = OrganizationSetting(
            organization_id=self.organization.id,
            pgw_sub_service_id=u'1234'
        )
        self.session.add(organization_setting)
        test_order = DummyModel(
            organization_id=self.organization.id,
            order_no=u'TEST000001',
            point_use_type=PointUseTypeEnum.NoUse
        )
        now = datetime.datetime.now()
        cancel.return_value = {
            u'resultType': api.PGW_API_RESULT_TYPE_PENDING
        }

        with self.assertRaises(PgwCardPaymentPluginFailure):
            plugin.cancel(request, test_order, now)

    @mock.patch('altair.app.ticketing.payments.plugins.dummy_pgw_api.cancel')
    def test_cancel_all_point_use(self, cancel):
        """ cancelの正常系テスト 全額ポイント払いによりスキップ """
        from altair.app.ticketing.core.models import OrganizationSetting, PointUseTypeEnum
        plugin = self._getTestTarget()

        request = DummyRequest()
        organization_setting = OrganizationSetting(
            organization_id=self.organization.id,
            pgw_sub_service_id=u'1234'
        )
        self.session.add(organization_setting)
        test_order = DummyModel(
            organization_id=self.organization.id,
            order_no=u'TEST000001',
            point_use_type=PointUseTypeEnum.AllUse
        )
        now = datetime.datetime.now()

        plugin.cancel(request, test_order, now)
        self.assertFalse(cancel.called)

    def test_cancel_no_sub_service_id(self):
        """ cancelの準正常系テスト Org設定にpgw_sub_service_idなし """
        from altair.app.ticketing.core.models import OrganizationSetting, PointUseTypeEnum
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure
        plugin = self._getTestTarget()

        request = DummyRequest()
        organization_setting = OrganizationSetting(
            organization_id=self.organization.id
        )
        self.session.add(organization_setting)
        test_order = DummyModel(
            organization_id=self.organization.id,
            order_no=u'TEST000001',
            point_use_type=PointUseTypeEnum.NoUse
        )
        now = datetime.datetime.now()

        with self.assertRaises(PgwCardPaymentPluginFailure):
            plugin.cancel(request, test_order, now)

    def test_refresh(self):
        """ refreshの正常系テスト """
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order = {}
        plugin.refresh(request, test_order)

    def test_refund(self):
        """ refundの正常系テスト """
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order = {}
        test_refund_record = {}
        plugin.refund(request, test_order, test_refund_record)

    def test_get_order_info(self):
        """ get_order_infoの正常系テスト """
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order = {}
        plugin.get_order_info(request, test_order)
