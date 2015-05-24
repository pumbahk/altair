# -*- coding: utf-8 -*-
from unittest import skip
import mock
from pyramid.testing import (
    DummyModel,
    DummyRequest,
    DummyResource,
    )
from altair.app.ticketing.famiport.tests import FamiPortTestCase


class FamiPortPaymentPluginTestMixin(object):

    def assert_valid_famiport_order(self, famiport_order, order_like, plugin):
        # playGuildeId: クライアントID (varchar(24))
        self.assertEqual(
            famiport_order.playguide_id,
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
            famiport_order.barcode_no,
            barcode_no,
            '支払番号',
            )

        # totalAmount: 合計金額(実際に店頭で支払う金額) (integer(8))
        total_amount = order_like.total_amount if plugin._in_payment else 0
        self.assertEqual(
            famiport_order.total_amount,
            total_amount,
            '合計金額(実際に店頭で支払う金額)',
            )

        # ticketPayment: チケット料金(代済は0になる) (integer(8))
        ticket_payment = 0
        if plugin._in_payment:
            ticket_payment = order_like.total_amount - \
                (order_like.system_fee + order_like.transaction_fee + order_like.delivery_fee + order_like.special_fee)
        self.assertEqual(
            famiport_order.ticket_payment,
            ticket_payment,
            'チケット料金(代済は0になる)',
            )

        # systemFee: システム利用料(代済は0になる) (integer(8))
        system_fee = order_like.system_fee + order_like.special_fee if plugin._in_payment else 0
        self.assertEqual(
            famiport_order.system_fee,
            system_fee,
            'システム利用料(代済は0になる)',
            )

        # ticketingFee: 店頭発券手数料 (integer(8))
        ticketing_fee = order_like.delivery_fee if plugin._in_payment else 0
        self.assertEqual(
            famiport_order.ticketing_fee,
            ticketing_fee,
            '店頭発券手数料',
            )
        # ticketCountTotal: 副券含む枚数 (integer(2))
        ticket_total_count = sum(
            ordered_product.product.num_tickets(order_like.payment_delivery_pair)
            for ordered_product in order_like.items
            )
        self.assertEqual(
            famiport_order.ticket_total_count,
            ticket_total_count,
            '発券枚数 (副券を含む)',
            )

        # ticketCount: 副券含まない枚数 (integer(2))
        ticket_count = sum(
            ordered_product.product.num_principal_tickets(order_like.payment_delivery_pair)
            for ordered_product in order_like.items
            )
        self.assertEqual(
            famiport_order.ticket_count,
            ticket_count,
            '発券枚数 (副券を含まない)',
            )

        # kogyoName: 興行名 (varchar(40))
        self.assertEqual(
            famiport_order.kogyo_name,
            order_like.sales_segment.event.title,
            '興行名',
            )

        # koenDate: 公演日時 (datetime(12))
        self.assertEqual(
            famiport_order.koen_date,
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
            famiport_order.phone_number,
            (order_like.shipping_address.tel_1 or order_like.shipping_address.tel_2).replace('-', '')
            )

        # nameInput: 指名要求フラグ (integer(1))
        self.assertEqual(
            famiport_order.name_input,
            order_like.organization.famiport_tenant.nameInput,
            'FamiPortTenant.nameInputを使う',
            )

        # phoneInput: 電話番号要求フラグ (integer(1))
        self.assertEqual(
            famiport_order.phone_input,
            order_like.organization.famiport_tenant.phoneInput,
            'FamiPortTenant.phoneInputを使う',
            )


class FamiPortPaymentPluginTest(FamiPortTestCase, FamiPortPaymentPluginTestMixin):
    def _target(self):
        from .famiport import FamiPortPaymentPlugin
        return FamiPortPaymentPlugin

    def _makeOne(self, *args, **kwds):
        target = self._target()
        return target(*args, **kwds)

    def _callFUT(self, func, *args, **kwds):
        return func(*args, **kwds)

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

    def test_prepare(self):
        """前処理"""
        request = DummyRequest()
        cart = DummyModel()
        plugin = self._makeOne()
        res = self._callFUT(plugin.prepare, request, cart)
        self.assert_(res is None)

    @skip('unimpl')
    def test_finish(self):
        """確定処理成功"""
        request = DummyRequest()
        plugin = self._makeOne()
        for cart in self.carts:
            res = self._callFUT(plugin.finish, request, cart)
            self.assert_(res is None)

    def test_finish2_success(self):
        """確定処理2成功"""
        request = DummyRequest()
        plugin = self._makeOne()
        for order in self.orders:
            famiport_order = self._callFUT(plugin.finish2, request, order.cart)
            self.assert_valid_famiport_order(famiport_order, order, plugin)

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


class FamiPortDeliveryPluginTest(FamiPortTestCase, FamiPortPaymentPluginTestMixin):
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
            famiport_order = self._callFUT(plugin.finish2, request, order.cart)
            self.assert_valid_famiport_order(famiport_order, order, plugin)

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


class FamiPortPaymentDeliveryPluginTest(FamiPortTestCase, FamiPortPaymentPluginTestMixin):
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
            famiport_order = self._callFUT(plugin.finish2, request, order.cart)
            self.assert_valid_famiport_order(famiport_order, order, plugin)

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


class FamiPortViewletTest(FamiPortTestCase):
    def _target(self):
        from .famiport import FamiPortPaymentDeliveryPlugin
        return FamiPortPaymentDeliveryPlugin

    def _callFUT(self, *args, **kwds):
        func = self._target()
        return func(*args, **kwds)


class FamiPortDeliveryConfirmViewletTest(FamiPortViewletTest):
    def _target(self):
        from .famiport import deliver_confirm_viewlet as func
        return func

    def _test_it(self):
        return
        # res = self._callFUT()
        self.fail()


class FamiPortDeliveryCompletionViewletTest(FamiPortViewletTest):
    def _target(self):
        from .famiport import deliver_completion_viewlet as func
        return func

    def test_it(self):
        name = u'ファミポート'
        description = u'説明説明説明説明説明'
        delivery_method = DummyModel(
            name=name,
            description=description,
            )
        payment_delivery_pair = DummyModel(delivery_method=delivery_method)
        order = DummyModel(payment_delivery_pair=payment_delivery_pair)
        context = DummyResource(
            order=order,
            description=delivery_method.description,
            )
        request = DummyRequest()

        res = self._callFUT(context, request)
        self.assertEqual(res, {
            'delivery_name': name,
            'description': description,
            })
