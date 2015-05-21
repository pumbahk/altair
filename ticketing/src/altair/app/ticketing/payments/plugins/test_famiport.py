# -*- coding: utf-8 -*-
from datetime import datetime
from unittest import (
    skip,
    TestCase,
    )
import mock
from pyramid.testing import (
    setUp,
    tearDown,
    DummyModel,
    DummyRequest,
    )
from altair.app.ticketing.testing import (
    _setup_db,
    _teardown_db,
    )
from altair.app.ticketing.core.testing import CoreTestMixin
from altair.app.ticketing.cart.testing import CartTestMixin


class FamiPortPaymentPluginTestMixin(object):
    now = datetime(2013, 1, 1, 0, 0, 0)

    def setup_dummy_data(self):
        self.session = _setup_db([
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.orders.models',
            'altair.app.ticketing.famiport.models',
            'altair.app.ticketing.cart.models',
            'altair.app.ticketing.lots.models',
            ])
        self.request = DummyRequest()
        self.config = setUp(request=self.request, settings={
            })
        self.config.include('altair.app.ticketing.famiport')
        self.config.include('altair.app.ticketing.formatter')
        self.result = {}

        from altair.app.ticketing.core.models import (
            CartMixin,
            DateCalculationBase
            )

        class DummyCart(CartMixin):
            def __init__(self, sales_segment, payment_delivery_pair, created_at):
                self.sales_segment = sales_segment
                self.payment_delivery_pair = payment_delivery_pair
                self.created_at = created_at

        self.pdmps = [
            DummyModel(
                issuing_start_day_calculation_base=DateCalculationBase.Absolute.v,
                issuing_interval_days=None,
                issuing_start_at=datetime(2013, 1, 5, 0, 0, 0),
                issuing_end_day_calculation_base=DateCalculationBase.Absolute.v,
                issuing_end_in_days=None,
                issuing_end_at=datetime(2013, 1, 8, 0, 0, 0),
                payment_start_day_calculation_base=DateCalculationBase.OrderDate.v,
                payment_start_in_days=0,
                payment_start_at=None,
                payment_due_day_calculation_base=DateCalculationBase.OrderDate.v,
                payment_period_days=1,
                payment_due_at=None
                ),
            DummyModel(
                issuing_start_day_calculation_base=DateCalculationBase.Absolute.v,
                issuing_interval_days=None,
                issuing_start_at=datetime(2013, 1, 5, 0, 0, 0),
                issuing_end_day_calculation_base=DateCalculationBase.Absolute.v,
                issuing_end_in_days=None,
                issuing_end_at=None,
                payment_start_day_calculation_base=DateCalculationBase.OrderDate.v,
                payment_start_in_days=0,
                payment_start_at=None,
                payment_due_day_calculation_base=DateCalculationBase.OrderDate.v,
                payment_period_days=1,
                payment_due_at=None
                ),
            DummyModel(
                issuing_start_day_calculation_base=DateCalculationBase.OrderDate.v,
                issuing_interval_days=3,
                issuing_start_at=None,
                issuing_end_day_calculation_base=DateCalculationBase.Absolute.v,
                issuing_end_in_days=None,
                issuing_end_at=datetime(2013, 1, 8, 0, 0, 0),
                payment_start_day_calculation_base=DateCalculationBase.OrderDate.v,
                payment_start_in_days=0,
                payment_start_at=None,
                payment_due_day_calculation_base=DateCalculationBase.OrderDate.v,
                payment_period_days=1,
                payment_due_at=None
                ),
            DummyModel(
                issuing_start_day_calculation_base=DateCalculationBase.Absolute.v,
                issuing_start_at=datetime(2013, 1, 5, 0, 0, 0),
                issuing_interval_days=None,
                issuing_end_day_calculation_base=DateCalculationBase.Absolute.v,
                issuing_end_in_days=None,
                issuing_end_at=datetime(2013, 1, 8, 0, 0, 0),
                payment_start_day_calculation_base=DateCalculationBase.OrderDate.v,
                payment_start_in_days=0,
                payment_start_at=None,
                payment_due_day_calculation_base=DateCalculationBase.OrderDate.v,
                payment_period_days=3,
                payment_due_at=None
                ),
            ]

        self.shipping_addresses = [
            DummyModel(
                first_name=u'first_name',
                last_name=u'last_name',
                first_name_kana=u'first_name_kana',
                last_name_kana=u'last_name_kana',
                tel_1=u'03-0000-0000',
                tel_2=u'03-0000-0001',
                zip=u'123-4567',
                email_1=u'test1@test.com',
                email_2=u'test2@test.com'
                ),
            DummyModel(
                first_name=u'first_name',
                last_name=u'last_name',
                first_name_kana=u'first_name_kana',
                last_name_kana=u'last_name_kana',
                tel_1=u'03-0000-0000',
                tel_2=u'03-0000-0001',
                zip=u'123-4567',
                email_1=u'test1@test.com',
                email_2=None
                ),
            DummyModel(
                first_name=u'first_name',
                last_name=u'last_name',
                first_name_kana=u'first_name_kana',
                last_name_kana=u'last_name_kana',
                tel_1=u'03-0000-0000',
                tel_2=u'03-0000-0001',
                zip=u'123-4567',
                email_1=None,
                email_2=u'test2@test.com'
                ),
            DummyModel(
                first_name=u'first_name',
                last_name=u'last_name',
                first_name_kana=u'first_name_kana',
                last_name_kana=u'last_name_kana',
                tel_1=u'03-0000-0000',
                tel_2=None,
                zip=u'123-4567',
                email_1=u'test1@test.com',
                email_2=u'test2@test.com'
                ),
            DummyModel(
                first_name=u'first_name',
                last_name=u'last_name',
                first_name_kana=u'first_name_kana',
                last_name_kana=u'last_name_kana',
                tel_1=None,
                tel_2=u'03-0000-0001',
                zip=u'123-4567',
                email_1=u'test1@test.com',
                email_2=u'test2@test.com'
                ),
            DummyModel(
                first_name=u'first_name',
                last_name=u'last_name',
                first_name_kana=u'first_name_kana',
                last_name_kana=u'last_name_kana',
                tel_1=u'03-0000-0000',
                tel_2=u'03-0000-0001',
                zip=None,
                email_1=u'test1@test.com',
                email_2=u'test2@test.com'
                ),
            ]

        self.famiport_tenant = DummyModel(
            playGuideId='',
            phoneInput=0,
            nameInput=0,
            )

        self.organization = DummyModel(
            code='XX',
            famiport_tenant=self.famiport_tenant,
            )

        orders = []

        for ii, payment_delivery_pair in enumerate(self.pdmps):
            for shipping_address in self.shipping_addresses:
                sales_segment = DummyModel(
                    event=DummyModel(
                        title=u'event title日本語日本語日本語'
                        ),
                    performance=DummyModel(
                        start_on=datetime(2013, 3, 1, 1, 2, 3),
                        end_on=datetime(2013, 3, 1, 2, 3, 4),
                        event=DummyModel(
                            title=u'event title日本語日本語日本語'
                            ),
                        )
                    )
                cart = DummyCart(sales_segment, payment_delivery_pair, self.now)
                orders.append(
                    DummyModel(
                        order_no='00000001',
                        shipping_address=shipping_address,
                        payment_delivery_pairo=payment_delivery_pair,
                        total_amount=1000,
                        system_fee=300,
                        transaction_fee=400,
                        delivery_fee=200,
                        special_fee=1,
                        issuing_start_at=cart.issuing_start_at,
                        issuing_end_at=cart.issuing_end_at,
                        payment_start_at=cart.payment_start_at,
                        payment_due_at=cart.payment_due_at,
                        sales_segment=sales_segment,
                        organization=self.organization,
                        paid_at=(datetime.now() if ii % 2 else None),
                        )
                    )
        self.orders = orders

    def tearDown(self):
        tearDown()
        self.session.remove()
        _teardown_db()

    def assert_valid_famiport_order(self, famiport_order, order_like):
        # playGuildeId: クライアントID (varchar(24))
        self.assertEqual(
            famiport_order.playGuideId,
            self.organization.famiport_tenant.playGuideId,
            'プレイガイド固有の画像を表示させる時のみ使う',
            )

        # barCodeNo: 支払い番号 (char(8))
        from altair.app.ticketing.famiport.models import FamiPortOrderNoSequence
        from altair.app.ticketing.utils import sensible_alnum_encode
        no_sequence = self.session.query(FamiPortOrderNoSequence) \
            .order_by(FamiPortOrderNoSequence.id.desc()) \
            .first()
        barcode_no = self.organization.code + sensible_alnum_encode(no_sequence.id).zfill(11)
        self.assertEqual(
            famiport_order.barCodeNo,
            barcode_no,
            '支払番号',
            )

        # totalAmount: 合計金額(実際に店頭で支払う金額) (integer(8))
        total_amount = 0 if order_like.paid_at else order_like.total_amount
        self.assertEqual(
            famiport_order.totalAmount,
            total_amount,
            '合計金額(実際に店頭で支払う金額)',
            )

        # ticketPayment: チケット料金(代済は0になる) (integer(8))
        ticket_payment = 0 if order_like.paid_at else order_like.total_amount - \
            (order_like.system_fee + order_like.transaction_fee + order_like.delivery_fee + order_like.special_fee)
        self.assertEqual(
            famiport_order.ticketPayment,
            ticket_payment,
            'チケット料金(代済は0になる)',
            )

        # systemFee: システム利用料(代済は0になる) (integer(8))
        system_fee = 0 if order_like.paid_at else order_like.system_fee
        self.assertEqual(
            famiport_order.systemFee,
            system_fee,
            'システム利用料(代済は0になる)',
            )

        # ticketingFee: 店頭発券手数料 (integer(8))
        ticketing_fee = 0 if order_like.paid_at else order_like.delivery_fee
        self.assertEqual(
            famiport_order.ticketingFee,
            ticketing_fee,
            '店頭発券手数料',
            )

        # ticketCountTotal: 副券含む枚数 (integer(2))
        ticket_total_count = sum(
            ordered_product.product.num_tickets(order_like.payment_delivery_pair)
            for ordered_product in order_like.items()
            )
        self.assertEqual(
            famiport_order.ticketTotalCount,
            ticket_total_count,
            '発券枚数 (副券を含む)',
            )

        # ticketCount: 副券含まない枚数 (integer(2))
        ticket_count = sum(
            ordered_product.product.num_principal_tickets(order_like.payment_delivery_pair)
            for ordered_product in order_like.items()
            )
        self.assertEqual(
            famiport_order.ticketCount,
            ticket_count,
            '発券枚数 (副券を含まない)',
            )

        # kogyoName: 興行名 (varchar(40))
        self.assertEqual(
            famiport_order.kogyoName,
            order_like.sales_segment.event.title,
            '興行名',
            )

        # koenDate: 公演日時 (datetime(12))
        self.assertEqual(
            famiport_order.koenDate,
            order_like.sales_segment.performance.start_on,
            'Performance.start_onを使う',
            )

        # name: お客様指名 (varchar(42))
        self.assertEqual(
            famiport_order.name,
            order_like.shipping_address.last_name + order_like.shipping_address.first_name,
            '氏名はShippingAddressのlast_nameとfirst_nameをつなげたものにする',
            )

        # phoneNumber: お客様指名 (varchar())
        self.assertEqual(
            famiport_order.phoneNumber,
            (order_like.shipping_address.tel_1 or order_like.shipping_address.tel_2).replace('-', '')
            )

        # nameInput: 指名要求フラグ (integer(1))
        self.assertEqual(
            famiport_order.nameInput,
            order_like.organization.famiport_tenant.nameInput,
            'FamiPortTenant.nameInputを使う',
            )

        # phoneInput: 電話番号要求フラグ (integer(1))
        self.assertEqual(
            famiport_order.phoneInput,
            order_like.organization.famiport_tenant.phoneInput,
            'FamiPortTenant.phoneInputを使う',
            )


class FamiPortPaymentPluginTest(TestCase, CoreTestMixin, CartTestMixin, FamiPortPaymentPluginTestMixin):
    def setUp(self):
        self.setup_dummy_data()

    def _target(self):
        from .famiport import FamiPortPaymentPlugin
        return FamiPortPaymentPlugin

    def _makeOne(self, *args, **kwds):
        target = self._target()
        return target(*args, **kwds)

    def _callFUT(self, func, *args, **kwds):
        return func(*args, **kwds)

    @skip('uninplemented')
    def test_validate_order_success(self):
        """FamiPortOrder作成可能なorder_like"""
        request = DummyRequest()
        cart = DummyModel()
        plugin = self._makeOne()
        res = self._callFUT(plugin.validate_order, request, cart)
        self.assert_(res is None)

    @skip('uninplemented')
    def test_validate_order_fail(self):
        """FamiPortOrder作成できないorder_like"""
        from ..exceptions import OrderLikeValidationFailure
        request = DummyRequest()
        cart = DummyModel()
        plugin = self._makeOne()
        with self.assertRailses(OrderLikeValidationFailure):
            self._callFUT(plugin.validate_order, request, cart)

    @skip('uninplemented')
    def test_prepare(self):
        """前処理"""
        request = DummyRequest()
        cart = DummyModel()
        plugin = self._makeOne()
        res = self._callFUT(plugin.prepare, request, cart)
        self.assert_(res is None)

    @skip('uninplemented')
    def test_finish(self):
        """確定処理成功"""
        request = DummyRequest()
        cart = DummyModel()
        plugin = self._makeOne()
        res = self._callFUT(plugin.finish, request, cart)
        self.assert_(res is None)

    def test_finish2_success(self):
        """確定処理2成功"""
        request = DummyRequest()
        plugin = self._makeOne()
        for order in self.orders:
            famiport_order = self._callFUT(plugin.finish2, request, order)
            self.assert_valid_famiport_order(famiport_order, order)

    @skip('uninplemented')
    def test_finish2_fail(self):
        """確定処理2失敗"""
        from altair.app.ticketing.famiport.exc import FamiPortError
        request = DummyRequest()
        cart = DummyModel()
        plugin = self._makeOne()

        with self.assertRaises(FamiPortError):
            self._callFUT(plugin.finish2, request, cart)

    @skip('uninplemented')
    def test_finished_true(self):
        """支払状態遷移済みなFamiPortOrder"""
        request = DummyRequest()
        cart = DummyModel()
        plugin = self._makeOne()

        res = self._callFUT(plugin.finished, request, cart)
        self.assert_(res)

    @skip('uninplemented')
    def test_finished_false(self):
        """支払状態遷移済みでないFamiPortOrder"""
        request = DummyRequest()
        order = DummyModel()
        plugin = self._makeOne()
        res = self._callFUT(plugin.finished, request, order)
        self.assert_(res is None)

    @skip('uninplemented')
    def test_refresh_success(self):
        """FamiPortOrder更新成功"""
        request = DummyRequest()
        order = DummyModel()
        plugin = self._makeOne()
        res = self._callFUT(plugin.refresh, request, order)
        self.assert_(res is None)

    @skip('uninplemented')
    def test_refresh_fail(self):
        """FamiPortOrder更新失敗"""
        from .famiport import FamiPortPluginFailure
        request = DummyRequest()
        order = DummyModel()
        plugin = self._makeOne()
        with self.assertRaises(FamiPortPluginFailure):
            self._callFUT(plugin.refresh, request, order)

    @skip('uninplemented')
    def test_cancel_success(self):
        """キャンセル成功"""
        request = DummyRequest()
        cart = DummyModel()
        plugin = self._makeOne()
        res = self._callFUT(plugin.cancel, request, cart)
        self.assert_(res is None)

    @skip('uninplemented')
    def test_cancel_fail(self):
        """キャンセル失敗"""
        from .famiport import FamiPortPluginFailure
        request = DummyRequest()
        cart = DummyModel()
        plugin = self._makeOne()
        with self.assertRaises(FamiPortPluginFailure):
            self._callFUT(plugin.cancel, request, cart)

    @skip('uninplemented')
    def test_refund_success(self):
        """払い戻し成功"""
        request = DummyRequest()
        order = DummyModel()
        plugin = self._makeOne()
        record = mock.Mock()
        res = self._callFUT(plugin.test_refund, request, order, record)
        self.assert_(res is None)

    @skip('uninplemented')
    def test_refund_fail(self):
        """払い戻し失敗"""
        from .famiport import FamiPortPluginFailure
        request = DummyRequest()
        order = DummyModel()
        plugin = self._makeOne()
        record = mock.Mock()
        with self.assertRaises(FamiPortPluginFailure):
            self._callFUT(plugin.refund, request, order, record)


class FamiPortDeliveryPluginTest(TestCase, CoreTestMixin, CartTestMixin, FamiPortPaymentPluginTestMixin):
    def setUp(self):
        self.setup_dummy_data()

    def _target(self):
        from .famiport import FamiPortDeliveryPlugin
        return FamiPortDeliveryPlugin

    def _makeOne(self, *args, **kwds):
        target = self._target()
        return target(*args, **kwds)

    def _callFUT(self, func, *args, **kwds):
        return func(*args, **kwds)

    @skip('uninplemented')
    def test_validate_order_success(self):
        """FamiPortOrder作成可能なorder_like"""
        request = DummyRequest()
        cart = DummyModel()
        plugin = self._makeOne()
        res = self._callFUT(plugin.validate_order, request, cart)
        self.assert_(res is None)

    @skip('uninplemented')
    def test_validate_order_fail(self):
        """FamiPortOrder作成できないorder_like"""
        from ..exceptions import OrderLikeValidationFailure
        request = DummyRequest()
        cart = DummyModel()
        plugin = self._makeOne()
        with self.assertRailses(OrderLikeValidationFailure):
            self._callFUT(plugin.validate_order, request, cart)

    @skip('uninplemented')
    def test_prepare(self):
        """前処理"""
        request = DummyRequest()
        cart = DummyModel()
        plugin = self._makeOne()
        res = self._callFUT(plugin.prepare, request, cart)
        self.assert_(res is None)

    @skip('uninplemented')
    def test_finish(self):
        """確定処理成功"""
        request = DummyRequest()
        cart = DummyModel()
        plugin = self._makeOne()
        res = self._callFUT(plugin.finish, request, cart)
        self.assert_(res is None)

    def test_finish2_success(self):
        """確定処理2成功"""
        request = DummyRequest()
        plugin = self._makeOne()
        for order in self.orders:
            famiport_order = self._callFUT(plugin.finish2, request, order)
            self.assert_valid_famiport_order(famiport_order, order)

    @skip('uninplemented')
    def test_finish2_fail(self):
        """確定処理2失敗"""
        from altair.app.ticketing.famiport.exc import FamiPortError
        request = DummyRequest()
        cart = DummyModel()
        plugin = self._makeOne()

        with self.assertRaises(FamiPortError):
            self._callFUT(plugin.finish2, request, cart)

    @skip('uninplemented')
    def test_finished_true(self):
        """支払状態遷移済みなFamiPortOrder"""
        request = DummyRequest()
        cart = DummyModel()
        plugin = self._makeOne()

        res = self._callFUT(plugin.finished, request, cart)
        self.assert_(res)

    @skip('uninplemented')
    def test_finished_false(self):
        """支払状態遷移済みでないFamiPortOrder"""
        request = DummyRequest()
        order = DummyModel()
        plugin = self._makeOne()
        res = self._callFUT(plugin.finished, request, order)
        self.assert_(res is None)

    @skip('uninplemented')
    def test_refresh_success(self):
        """FamiPortOrder更新成功"""
        request = DummyRequest()
        order = DummyModel()
        plugin = self._makeOne()
        res = self._callFUT(plugin.refresh, request, order)
        self.assert_(res is None)

    @skip('uninplemented')
    def test_refresh_fail(self):
        """FamiPortOrder更新失敗"""
        from .famiport import FamiPortPluginFailure
        request = DummyRequest()
        order = DummyModel()
        plugin = self._makeOne()
        with self.assertRaises(FamiPortPluginFailure):
            self._callFUT(plugin.refresh, request, order)

    @skip('uninplemented')
    def test_cancel_success(self):
        """キャンセル成功"""
        request = DummyRequest()
        cart = DummyModel()
        plugin = self._makeOne()
        res = self._callFUT(plugin.cancel, request, cart)
        self.assert_(res is None)

    @skip('uninplemented')
    def test_cancel_fail(self):
        """キャンセル失敗"""
        from .famiport import FamiPortPluginFailure
        request = DummyRequest()
        cart = DummyModel()
        plugin = self._makeOne()
        with self.assertRaises(FamiPortPluginFailure):
            self._callFUT(plugin.cancel, request, cart)

    @skip('uninplemented')
    def test_refund_success(self):
        """払い戻し成功"""
        request = DummyRequest()
        order = DummyModel()
        plugin = self._makeOne()
        record = mock.Mock()
        res = self._callFUT(plugin.test_refund, request, order, record)
        self.assert_(res is None)

    @skip('uninplemented')
    def test_refund_fail(self):
        """払い戻し失敗"""
        from .famiport import FamiPortPluginFailure
        request = DummyRequest()
        order = DummyModel()
        plugin = self._makeOne()
        record = mock.Mock()
        with self.assertRaises(FamiPortPluginFailure):
            self._callFUT(plugin.refund, request, order, record)


class FamiPortPaymentDeliveryPluginTest(TestCase, CoreTestMixin, CartTestMixin, FamiPortPaymentPluginTestMixin):
    def setUp(self):
        self.setup_dummy_data()

    def _target(self):
        from .famiport import FamiPortPaymentDeliveryPlugin
        return FamiPortPaymentDeliveryPlugin

    def _makeOne(self, *args, **kwds):
        target = self._target()
        return target(*args, **kwds)

    def _callFUT(self, func, *args, **kwds):
        return func(*args, **kwds)

    @skip('uninplemented')
    def test_validate_order_success(self):
        """FamiPortOrder作成可能なorder_like"""
        request = DummyRequest()
        cart = DummyModel()
        plugin = self._makeOne()
        res = self._callFUT(plugin.validate_order, request, cart)
        self.assert_(res is None)

    @skip('uninplemented')
    def test_validate_order_fail(self):
        """FamiPortOrder作成できないorder_like"""
        from ..exceptions import OrderLikeValidationFailure
        request = DummyRequest()
        cart = DummyModel()
        plugin = self._makeOne()
        with self.assertRailses(OrderLikeValidationFailure):
            self._callFUT(plugin.validate_order, request, cart)

    @skip('uninplemented')
    def test_prepare(self):
        """前処理"""
        request = DummyRequest()
        cart = DummyModel()
        plugin = self._makeOne()
        res = self._callFUT(plugin.prepare, request, cart)
        self.assert_(res is None)

    @skip('uninplemented')
    def test_finish(self):
        """確定処理成功"""
        request = DummyRequest()
        cart = DummyModel()
        plugin = self._makeOne()
        res = self._callFUT(plugin.finish, request, cart)
        self.assert_(res is None)

    def test_finish2_success(self):
        """確定処理2成功"""
        request = DummyRequest()
        plugin = self._makeOne()
        for order in self.orders:
            famiport_order = self._callFUT(plugin.finish2, request, order)
            self.assert_valid_famiport_order(famiport_order, order)

    @skip('uninplemented')
    def test_finish2_fail(self):
        """確定処理2失敗"""
        from altair.app.ticketing.famiport.exc import FamiPortError
        request = DummyRequest()
        cart = DummyModel()
        plugin = self._makeOne()

        with self.assertRaises(FamiPortError):
            self._callFUT(plugin.finish2, request, cart)

    @skip('uninplemented')
    def test_finished_true(self):
        """支払状態遷移済みなFamiPortOrder"""
        request = DummyRequest()
        cart = DummyModel()
        plugin = self._makeOne()

        res = self._callFUT(plugin.finished, request, cart)
        self.assert_(res)

    @skip('uninplemented')
    def test_finished_false(self):
        """支払状態遷移済みでないFamiPortOrder"""
        request = DummyRequest()
        order = DummyModel()
        plugin = self._makeOne()
        res = self._callFUT(plugin.finished, request, order)
        self.assert_(res is None)

    @skip('uninplemented')
    def test_refresh_success(self):
        """FamiPortOrder更新成功"""
        request = DummyRequest()
        order = DummyModel()
        plugin = self._makeOne()
        res = self._callFUT(plugin.refresh, request, order)
        self.assert_(res is None)

    @skip('uninplemented')
    def test_refresh_fail(self):
        """FamiPortOrder更新失敗"""
        from .famiport import FamiPortPluginFailure
        request = DummyRequest()
        order = DummyModel()
        plugin = self._makeOne()
        with self.assertRaises(FamiPortPluginFailure):
            self._callFUT(plugin.refresh, request, order)

    @skip('uninplemented')
    def test_cancel_success(self):
        """キャンセル成功"""
        request = DummyRequest()
        cart = DummyModel()
        plugin = self._makeOne()
        res = self._callFUT(plugin.cancel, request, cart)
        self.assert_(res is None)

    @skip('uninplemented')
    def test_cancel_fail(self):
        """キャンセル失敗"""
        from .famiport import FamiPortPluginFailure
        request = DummyRequest()
        cart = DummyModel()
        plugin = self._makeOne()
        with self.assertRaises(FamiPortPluginFailure):
            self._callFUT(plugin.cancel, request, cart)

    @skip('uninplemented')
    def test_refund_success(self):
        """払い戻し成功"""
        request = DummyRequest()
        order = DummyModel()
        plugin = self._makeOne()
        record = mock.Mock()
        res = self._callFUT(plugin.test_refund, request, order, record)
        self.assert_(res is None)

    @skip('uninplemented')
    def test_refund_fail(self):
        """払い戻し失敗"""
        from .famiport import FamiPortPluginFailure
        request = DummyRequest()
        order = DummyModel()
        plugin = self._makeOne()
        record = mock.Mock()
        with self.assertRaises(FamiPortPluginFailure):
            self._callFUT(plugin.refund, request, order, record)
