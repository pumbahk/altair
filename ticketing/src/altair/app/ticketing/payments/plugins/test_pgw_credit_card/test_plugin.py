# -*- coding:utf-8 -*-

import unittest
import datetime
from altair.app.ticketing.testing import DummyRequest, _setup_db, _teardown_db
from altair.app.ticketing.core.testing import CoreTestMixin
from altair.app.ticketing.cart.testing import CartTestMixin
import mock
from pyramid.testing import DummyModel


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
        from .. import pgw_credit_card
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

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.authorize_and_capture')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_order_status')
    def test_finish_success_with_initialized_status(self, get_pgw_order_status, authorize_and_capture):
        """ finishの正常系テスト　決済処理成功_決済ステータス initialized """
        from altair.app.ticketing.pgw.models import PaymentStatusEnum
        plugin = self._getTestTarget()

        test_cart = self._create_base_test_cart()
        request = DummyRequest()
        get_pgw_order_status.return_value = DummyModel(
            gross_amount=test_cart.payment_amount,
            payment_status=PaymentStatusEnum.initialized.v
        )
        authorize_and_capture.return_value = None

        order = plugin.finish(request, test_cart)
        self.assertTrue(authorize_and_capture.called)
        self.assertIsNotNone(order)
        self.assertIsNotNone(order.paid_at)
        self.assertIsNotNone(test_cart.finished_at)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.authorize_and_capture')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_order_status')
    def test_finish_api_error_with_initialized_status(self, get_pgw_order_status, authorize_and_capture):
        """ finishの準正常系テスト　決済処理失敗_決済ステータス initialized """
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure, DummyPgwAPIError
        from altair.app.ticketing.pgw.models import PaymentStatusEnum
        plugin = self._getTestTarget()

        test_cart = self._create_base_test_cart()
        request = DummyRequest()
        get_pgw_order_status.return_value = DummyModel(
            gross_amount=test_cart.payment_amount,
            payment_status=PaymentStatusEnum.initialized.v
        )
        authorize_and_capture.side_effect = DummyPgwAPIError(error_code='test_error', error_message='testMessage')

        with self.assertRaises(PgwCardPaymentPluginFailure):
            plugin.finish(request, test_cart)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.capture')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_order_status')
    def test_finish_success_with_authorized_status(self, get_pgw_order_status, capture):
        """ finishの正常系テスト　決済処理成功_決済ステータス authorized """
        from altair.app.ticketing.pgw.models import PaymentStatusEnum
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_cart = self._create_base_test_cart()
        get_pgw_order_status.return_value = DummyModel(
            gross_amount=test_cart.payment_amount,
            payment_status=PaymentStatusEnum.auth.v
        )
        capture.return_value = None

        order = plugin.finish(request, test_cart)
        self.assertTrue(capture.called)
        self.assertIsNotNone(order)
        self.assertIsNotNone(order.paid_at)
        self.assertIsNotNone(test_cart.finished_at)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.capture')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_order_status')
    def test_finish_api_error_with_authorized_status(self, get_pgw_order_status, capture):
        """ finishの準正常系テスト　決済処理失敗_決済ステータス authorized """
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure, DummyPgwAPIError
        from altair.app.ticketing.pgw.models import PaymentStatusEnum
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_cart = self._create_base_test_cart()
        get_pgw_order_status.return_value = DummyModel(
            gross_amount=test_cart.payment_amount,
            payment_status=PaymentStatusEnum.auth.v
        )
        capture.side_effect = DummyPgwAPIError(error_code=u'test_error', error_message=u'testMessage')

        with self.assertRaises(PgwCardPaymentPluginFailure):
            plugin.finish(request, test_cart)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.capture')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.modify')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_order_status')
    def test_finish_success_with_authorized_status_and_modify_amount(self, get_pgw_order_status, modify, capture):
        """ finishの正常系テスト　決済処理成功_決済ステータス authorized オーソリ金額から減額あり """
        from altair.app.ticketing.pgw.models import PaymentStatusEnum
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_cart = self._create_base_test_cart()
        get_pgw_order_status.return_value = DummyModel(
            gross_amount=test_cart.payment_amount + 10,
            payment_status=PaymentStatusEnum.auth.v
        )
        modify.return_value = None
        capture.return_value = None

        order = plugin.finish(request, test_cart)
        self.assertTrue(modify.called)
        self.assertTrue(capture.called)
        self.assertIsNotNone(order)
        self.assertIsNotNone(order.paid_at)
        self.assertIsNotNone(test_cart.finished_at)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.capture')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.modify')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_order_status')
    def test_finish_api_error_with_authorized_status_and_modify_amount(self, get_pgw_order_status, modify, capture):
        """ finishの準正常系テスト　決済処理失敗_決済ステータス authorized オーソリ金額から減額あり """
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure, DummyPgwAPIError
        from altair.app.ticketing.pgw.models import PaymentStatusEnum
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_cart = self._create_base_test_cart()
        get_pgw_order_status.return_value = DummyModel(
            gross_amount=test_cart.payment_amount + 10,
            payment_status=PaymentStatusEnum.auth.v
        )
        modify.side_effect = DummyPgwAPIError(error_code=u'test_error', error_message=u'testMessage')

        with self.assertRaises(PgwCardPaymentPluginFailure):
            plugin.finish(request, test_cart)
        self.assertFalse(capture.called)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.modify')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_order_status')
    def test_finish_success_with_captured_status_and_modify_amount(self, get_pgw_order_status, modify):
        """ finishの正常系テスト　決済処理成功_決済ステータス captured 確定金額から減額あり """
        from altair.app.ticketing.pgw.models import PaymentStatusEnum
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_cart = self._create_base_test_cart()
        get_pgw_order_status.return_value = DummyModel(
            gross_amount=test_cart.payment_amount + 10,
            payment_status=PaymentStatusEnum.capture.v
        )
        modify.return_value = None

        order = plugin.finish(request, test_cart)
        self.assertTrue(modify.called)
        self.assertIsNotNone(order)
        self.assertIsNotNone(order.paid_at)
        self.assertIsNotNone(test_cart.finished_at)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.modify')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_order_status')
    def test_finish_failure_with_captured_status_and_modify_amount(self, get_pgw_order_status, modify):
        """ finishの準正常系テスト　決済処理失敗_決済ステータス captured 確定金額から減額あり """
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure, DummyPgwAPIError
        from altair.app.ticketing.pgw.models import PaymentStatusEnum
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_cart = self._create_base_test_cart()
        get_pgw_order_status.return_value = DummyModel(
            gross_amount=test_cart.payment_amount + 10,
            payment_status=PaymentStatusEnum.capture.v
        )
        modify.side_effect = DummyPgwAPIError(error_code=u'test_error', error_message='testMessage')

        with self.assertRaises(PgwCardPaymentPluginFailure):
            plugin.finish(request, test_cart)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.modify')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_order_status')
    def test_finish_success_with_captured_status_and_same_amount(self, get_pgw_order_status, modify):
        """ finishの正常系テスト　決済処理成功_決済ステータス captured 確定金額変更なし """
        from altair.app.ticketing.pgw.models import PaymentStatusEnum
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_cart = self._create_base_test_cart()
        get_pgw_order_status.return_value = DummyModel(
            gross_amount=test_cart.payment_amount,
            payment_status=PaymentStatusEnum.capture.v
        )

        order = plugin.finish(request, test_cart)
        self.assertIsNotNone(order)
        self.assertIsNotNone(order.paid_at)
        self.assertIsNotNone(test_cart.finished_at)
        self.assertFalse(modify.called)

    def test_finish_point_all_use(self):
        """ finishの正常系テスト 全額ポイント払いのため決済スキップ """
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_cart = self._create_base_test_cart()
        test_cart.point_amount = test_cart.total_amount

        order = plugin.finish(request, test_cart)
        self.assertIsNotNone(order)
        self.assertIsNotNone(order.paid_at)
        self.assertIsNotNone(test_cart.finished_at)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_order_status')
    def test_finish_invalid_payment_status_type(self, get_pgw_order_status):
        """ finishの異常系テスト 決済ステータスが不正 """
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure
        from altair.app.ticketing.pgw.models import PaymentStatusEnum
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_cart = self._create_base_test_cart()
        get_pgw_order_status.return_value = DummyModel(
            gross_amount=test_cart.payment_amount,
            payment_status=PaymentStatusEnum.cancel.v
        )
        with self.assertRaises(PgwCardPaymentPluginFailure):
            plugin.finish(request, test_cart)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_order_status')
    def test_finish_invalid_amount(self, get_pgw_order_status):
        """ finishの異常系テスト 決済額を増額に変更 """
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure
        from altair.app.ticketing.pgw.models import PaymentStatusEnum
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_cart = self._create_base_test_cart()
        get_pgw_order_status.return_value = DummyModel(
            gross_amount=test_cart.payment_amount - 10,
            payment_status=PaymentStatusEnum.auth.v
        )

        with self.assertRaises(PgwCardPaymentPluginFailure):
            plugin.finish(request, test_cart)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_order_status')
    def test_finish_unexpected_error(self, get_pgw_order_status):
        """ finishの異常系テスト 予期せぬ例外発生 """
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_cart = self._create_base_test_cart()
        get_pgw_order_status.side_effect = ValueError

        with self.assertRaises(PgwCardPaymentPluginFailure):
            plugin.finish(request, test_cart)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.authorize_and_capture')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_order_status')
    def test_finish2(self, get_pgw_order_status, authorize_and_capture):
        """ finish2の正常系テスト(大部分をfinishのテストで確認済みのため、正常系を1パターンのみ確認) """
        from altair.app.ticketing.pgw.models import PaymentStatusEnum
        plugin = self._getTestTarget()

        test_cart = self._create_base_test_cart()
        request = DummyRequest()
        get_pgw_order_status.return_value = DummyModel(
            gross_amount=test_cart.payment_amount,
            payment_status=PaymentStatusEnum.initialized.v
        )
        authorize_and_capture.return_value = None

        plugin.finish2(request, test_cart)
        self.assertTrue(get_pgw_order_status.called)
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

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.cancel_or_refund')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_status')
    def test_cancel_success(self, get_pgw_status, cancel_or_refund):
        """ cancelの正常系テスト キャンセル成功 """
        from altair.app.ticketing.core.models import PointUseTypeEnum
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order = DummyModel(
            organization_id=self.organization.id,
            order_no=u'TEST000001',
            point_use_type=PointUseTypeEnum.NoUse
        )
        now = datetime.datetime.now()
        get_pgw_status.return_value = {
            u'details': [
                {
                    u'paymentStatusType': u'captured'
                }
            ]
        }
        cancel_or_refund.return_value = {
            u'resultType': u'success'
        }

        plugin.cancel(request, test_order, now)
        self.assertTrue(cancel_or_refund.called)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.cancel_or_refund')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_status')
    def test_cancel_failure(self, get_pgw_status, cancel_or_refund):
        """ cancelの準正常系テスト キャンセル失敗 """
        from altair.app.ticketing.core.models import PointUseTypeEnum
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order = DummyModel(
            organization_id=self.organization.id,
            order_no=u'TEST000001',
            point_use_type=PointUseTypeEnum.NoUse
        )
        now = datetime.datetime.now()
        get_pgw_status.return_value = {
            u'details': [
                {
                    u'paymentStatusType': u'captured'
                }
            ]
        }
        cancel_or_refund.return_value = {
            u'resultType': u'failure',
            u'errorCode': u'test_error',
            u'errorMessage': u'testMessage'
        }

        with self.assertRaises(PgwCardPaymentPluginFailure):
            plugin.cancel(request, test_order, now)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.cancel_or_refund')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_status')
    def test_cancel_pending(self, get_pgw_status, cancel_or_refund):
        """ cancelの準正常系テスト キャンセルPending """
        from altair.app.ticketing.core.models import PointUseTypeEnum
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order = DummyModel(
            organization_id=self.organization.id,
            order_no=u'TEST000001',
            point_use_type=PointUseTypeEnum.NoUse
        )
        now = datetime.datetime.now()
        get_pgw_status.return_value = {
            u'details': [
                {
                    u'paymentStatusType': u'captured'
                }
            ]
        }
        cancel_or_refund.return_value = {
            u'resultType': u'pending',
            u'errorCode': u'test_error',
            u'errorMessage': u'testMessage'
        }

        with self.assertRaises(PgwCardPaymentPluginFailure):
            plugin.cancel(request, test_order, now)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.cancel_or_refund')
    def test_cancel_all_point_use(self, cancel_or_refund):
        """ cancelの正常系テスト 全額ポイント払いによりスキップ """
        from altair.app.ticketing.core.models import PointUseTypeEnum
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order = DummyModel(
            organization_id=self.organization.id,
            order_no=u'TEST000001',
            point_use_type=PointUseTypeEnum.AllUse
        )
        now = datetime.datetime.now()

        plugin.cancel(request, test_order, now)
        self.assertFalse(cancel_or_refund.called)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.cancel_or_refund')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_status')
    def test_cancel_invalid_payment_status_type(self, get_pgw_status, cancel_or_refund):
        """ cancelの異常系テスト 決済ステータス不正 """
        from altair.app.ticketing.core.models import PointUseTypeEnum
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order = DummyModel(
            organization_id=self.organization.id,
            order_no=u'TEST000001',
            point_use_type=PointUseTypeEnum.NoUse
        )
        now = datetime.datetime.now()
        get_pgw_status.return_value = {
            u'details': [
                {
                    u'paymentStatusType': u'initialized'
                }
            ]
        }

        with self.assertRaises(PgwCardPaymentPluginFailure):
            plugin.cancel(request, test_order, now)
        self.assertFalse(cancel_or_refund.called)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.modify')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_status')
    def test_refresh_success(self, get_pgw_status, modify):
        """ refreshの正常系テスト 金額更新成功"""
        from altair.app.ticketing.core.models import PointUseTypeEnum
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order = DummyModel(
            organization_id=self.organization.id,
            order_no=u'TEST000001',
            point_use_type=PointUseTypeEnum.NoUse,
            payment_amount=1000,
            point_amount=0,
            delivered_at=None
        )
        get_pgw_status.return_value = {
            u'details': [
                {
                    u'paymentStatusType': u'captured',
                    u'grossAmount': test_order.payment_amount + 100
                }
            ]
        }
        modify.return_value = {
            u'resultType': u'success'
        }
        plugin.refresh(request, test_order)
        self.assertTrue(modify.called)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.modify')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_status')
    def test_refresh_failure(self, get_pgw_status, modify):
        """ refreshの準正常系テスト 金額更新失敗"""
        from altair.app.ticketing.core.models import PointUseTypeEnum
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order = DummyModel(
            organization_id=self.organization.id,
            order_no=u'TEST000001',
            point_use_type=PointUseTypeEnum.NoUse,
            payment_amount=1000,
            point_amount=0,
            delivered_at=None
        )
        get_pgw_status.return_value = {
            u'details': [
                {
                    u'paymentStatusType': u'captured',
                    u'grossAmount': test_order.payment_amount + 100
                }
            ]
        }
        modify.return_value = {
            u'resultType': u'failure',
            u'errorCode': u'test_error',
            u'errorMessage': u'testMessage'
        }
        with self.assertRaises(PgwCardPaymentPluginFailure):
            plugin.refresh(request, test_order)
        self.assertTrue(modify.called)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.modify')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_status')
    def test_refresh_pending(self, get_pgw_status, modify):
        """ refreshの準正常系テスト 金額更新Pending"""
        from altair.app.ticketing.core.models import PointUseTypeEnum
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order = DummyModel(
            organization_id=self.organization.id,
            order_no=u'TEST000001',
            point_use_type=PointUseTypeEnum.NoUse,
            payment_amount=1000,
            point_amount=0,
            delivered_at=None
        )
        get_pgw_status.return_value = {
            u'details': [
                {
                    u'paymentStatusType': u'captured',
                    u'grossAmount': test_order.payment_amount + 100
                }
            ]
        }
        modify.return_value = {
            u'resultType': u'pending',
            u'errorCode': u'test_error',
            u'errorMessage': u'testMessage'
        }
        with self.assertRaises(PgwCardPaymentPluginFailure):
            plugin.refresh(request, test_order)
        self.assertTrue(modify.called)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.modify')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_status')
    def test_refresh_all_point_use(self, get_pgw_status, modify):
        """ refreshの正常系テスト 全額ポイント払いのためスキップ """
        from altair.app.ticketing.core.models import PointUseTypeEnum
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order = DummyModel(
            organization_id=self.organization.id,
            order_no=u'TEST000001',
            point_use_type=PointUseTypeEnum.AllUse,
            payment_amount=1000,
            point_amount=1000,
            delivered_at=None
        )
        plugin.refresh(request, test_order)
        self.assertFalse(get_pgw_status.called)
        self.assertFalse(modify.called)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.modify')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_status')
    def test_refresh_already_deliverd(self, get_pgw_status, modify):
        """ refreshの異常系テスト 発券済みのためエラー """
        from altair.app.ticketing.core.models import PointUseTypeEnum
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure
        from datetime import datetime
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order = DummyModel(
            organization_id=self.organization.id,
            order_no=u'TEST000001',
            point_use_type=PointUseTypeEnum.NoUse,
            payment_amount=1000,
            point_amount=0,
            delivered_at=datetime.now()
        )
        with self.assertRaises(PgwCardPaymentPluginFailure):
            plugin.refresh(request, test_order)
        self.assertFalse(get_pgw_status.called)
        self.assertFalse(modify.called)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.modify')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_status')
    def test_refresh_invalid_payment_status_type(self, get_pgw_status, modify):
        """ refreshの異常系テスト 決済ステータス不正 """
        from altair.app.ticketing.core.models import PointUseTypeEnum
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order = DummyModel(
            organization_id=self.organization.id,
            order_no=u'TEST000001',
            point_use_type=PointUseTypeEnum.NoUse,
            payment_amount=1000,
            point_amount=0,
            delivered_at=None
        )
        get_pgw_status.return_value = {
            u'details': [
                {
                    u'paymentStatusType': u'authorized',
                    u'grossAmount': test_order.payment_amount + 100
                }
            ]
        }
        with self.assertRaises(PgwCardPaymentPluginFailure):
            plugin.refresh(request, test_order)
        self.assertTrue(get_pgw_status.called)
        self.assertFalse(modify.called)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.modify')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_status')
    def test_refresh_same_amount(self, get_pgw_status, modify):
        """ refreshの正常系テスト 金額変更なしのためスキップ """
        from altair.app.ticketing.core.models import PointUseTypeEnum
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order = DummyModel(
            organization_id=self.organization.id,
            order_no=u'TEST000001',
            point_use_type=PointUseTypeEnum.NoUse,
            payment_amount=1000,
            point_amount=0,
            delivered_at=None
        )
        get_pgw_status.return_value = {
            u'details': [
                {
                    u'paymentStatusType': u'captured',
                    u'grossAmount': test_order.payment_amount
                }
            ]
        }
        plugin.refresh(request, test_order)
        self.assertTrue(get_pgw_status.called)
        self.assertFalse(modify.called)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.modify')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_status')
    def test_refresh_increased_amount(self, get_pgw_status, modify):
        """ refreshの異常系テスト 金額変更なしのためスキップ """
        from altair.app.ticketing.core.models import PointUseTypeEnum
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_order = DummyModel(
            organization_id=self.organization.id,
            order_no=u'TEST000001',
            point_use_type=PointUseTypeEnum.NoUse,
            payment_amount=1000,
            point_amount=0,
            delivered_at=None
        )
        get_pgw_status.return_value = {
            u'details': [
                {
                    u'paymentStatusType': u'captured',
                    u'grossAmount': test_order.payment_amount - 100
                }
            ]
        }
        with self.assertRaises(PgwCardPaymentPluginFailure):
            plugin.refresh(request, test_order)
        self.assertTrue(get_pgw_status.called)
        self.assertFalse(modify.called)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.modify')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_status')
    def test_refresh_changing_point_use_type(self, get_pgw_status, modify):
        """ refreshの異常系テスト ポイント決済種別を変更するような金額変更 """
        from altair.app.ticketing.core.models import PointUseTypeEnum
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure
        plugin = self._getTestTarget()

        request = DummyRequest()
        test_captured_amount=1500
        test_total_amount_to_refresh=999
        test_point_amount=1000
        test_order = DummyModel(
            organization_id=self.organization.id,
            order_no=u'TEST000001',
            point_use_type=PointUseTypeEnum.PartialUse,
            total_amount=test_total_amount_to_refresh,
            point_amount=test_point_amount,
            payment_amount=test_total_amount_to_refresh - test_point_amount,
            delivered_at=None
        )
        get_pgw_status.return_value = {
            u'details': [
                {
                    u'paymentStatusType': u'captured',
                    u'grossAmount': test_captured_amount
                }
            ]
        }
        with self.assertRaises(PgwCardPaymentPluginFailure):
            plugin.refresh(request, test_order)
        self.assertTrue(get_pgw_status.called)
        self.assertFalse(modify.called)

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
