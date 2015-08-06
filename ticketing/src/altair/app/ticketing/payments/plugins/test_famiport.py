# -*- coding: utf-8 -*-
"""ファミポート決済pluginテスト

支払番号: barCodeNo(13) 入金発券要求の「支払番号」にセットする番号で予約照会時に裁判
注文ID: orderId(12) 下9桁を管理番号として扱う（会計実績ファイルに出力）
払込票番号: orderTicketNo(13) 予済み場合は予約照会応答の「支払番号」
引換票番号: exchangeTicketNo(13) 後日予済アプリで発券するための予約番号予
予約番号: reserveNumber(13) 画面入力／QRコード／番号入力GWにより入力された予約番号
"""
from unittest import (
    skip,
    TestCase,
    )
import mock
from pyramid.testing import (
    DummyModel,
    DummyRequest,
    DummyResource,
    )
from altair.app.ticketing.famiport.communication.testing import FamiPortTestBase


class FamiPortTestCase(FamiPortTestBase, TestCase):
    pass


class FamiPortPaymentPluginTestMixin(object):

    def assert_valid_famiport_order(self, famiport_order, order_like, plugin):
        # playGuildeId: クライアントID (varchar(24))
        self.assertEqual(
            famiport_order.playguide_id,
            self.organization.famiport_tenant.playGuideId,
            'プレイガイド固有の画像を表示させる時のみ使う',
            )

        # barCodeNo: 支払い番号 (char(13))
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

        # orderId: 注文ID (char(13))
        self.assertEqual(len(famiport_order.famiport_order_identifier), 12,
                         '注文ID プレイガイド管理の注文識別ID (下9桁を管理番号として扱う（会計実績ファイルに出力)',
                         )

        # orderTicketNo: 払込票番号
        self.assertEqual(len(famiport_order.order_ticket_no), 13,
                         '払込票番号 予済み場合は予約照会応答の「支払番号」',
                         )

        # exchangeTiketNo: 引換票番号
        self.assertEqual(len(famiport_order.exchange_ticket_no), 13,
                         '後日予済アプリで発券するための予約番号予',
                         )

        # reserveNumber: 予約番号
        self.assertEqual(len(famiport_order.reserve_number), 13,
                         '画面入力／QRコード／番号入力GWにより入力された予約番号',
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
        system_fee = order_like.transaction_fee + order_like.system_fee + order_like.special_fee if plugin._in_payment else 0
        self.assertEqual(
            famiport_order.system_fee,
            system_fee,
            'システム利用料(代済は0になる) 決済手数料 + システム利用料 + 特別手数料になる (決済手数料の項目がないのでここに含める)',
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

        # name: お客様氏名 (varchar(42))
        self.assertEqual(
            famiport_order.name,
            order_like.shipping_address.last_name + order_like.shipping_address.first_name,
            '氏名はShippingAddressのlast_nameとfirst_nameをつなげたものにする',
            )

        # phoneNumber: お客様電話番号 (varchar())
        self.assertEqual(
            famiport_order.phone_number,
            (order_like.shipping_address.tel_1 or order_like.shipping_address.tel_2).replace('-', '')
            )

        # phoneNumber: お客様住所1 (varchar(200))
        address_1 = order_like.shipping_address.prefecture + order_like.shipping_address.city + order_like.shipping_address.address_1
        self.assertEqual(
            famiport_order.address_1,
            address_1,
            'お客様住所1',
            )

        # phoneNumber: お客様住所2 (varchar(200))
        address_2 = order_like.shipping_address.address_2
        self.assertEqual(
            famiport_order.address_2,
            address_2
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

        # 支払開始日時
        self.assertEqual(
            famiport_order.payment_start_at,
            order_like.payment_start_at,
            )

        # 支払期限
        self.assertEqual(
            famiport_order.payment_due_at,
            order_like.payment_due_at,
            )

        # 発券開始日時
        self.assertEqual(
            famiport_order.issuing_start_at,
            order_like.issuing_start_at,
            )

        # 発券終了日時
        self.assertEqual(
            famiport_order.issuing_end_at,
            order_like.issuing_end_at,
            )


class FamiPortPaymentPluginTest(FamiPortTestCase):
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

    @skip('orz')
    @mock.patch('altair.app.ticketing.payments.plugins.famiport.order_models.Order.create_from_cart')
    @mock.patch('altair.app.ticketing.payments.plugins.famiport.create_famiport_order')
    def test_finish(self, create_famiport_order, create_from_cart):
        """確定処理成功"""
        exp_order = create_from_cart.return_value = mock.Mock()
        create_famiport_order.return_value = mock.Mock()
        request = DummyRequest()
        cart = self.orders[0].cart
        plugin = self._makeOne()

        order = plugin.finish(request, cart)
        exp_call_args_create_famiport_order = mock.call(request, exp_order, plugin=plugin, in_payment=False)

        self.assertEqual(order, exp_order)
        self.assertTrue(create_famiport_order.called)
        self.assertEqual(create_famiport_order.call_args, exp_call_args_create_famiport_order)

    @mock.patch('altair.app.ticketing.payments.plugins.famiport.build_ticket_dicts_from_order_like')
    @mock.patch('altair.app.ticketing.payments.plugins.famiport.build_famiport_order_dict')
    @mock.patch('altair.app.ticketing.payments.plugins.famiport.lookup_famiport_tenant')
    @mock.patch('altair.app.ticketing.payments.plugins.famiport.create_famiport_order')
    def test_finish2_success(self, create_famiport_order, lookup_famiport_tenant,
                             build_famiport_order_dict, build_ticket_dicts_from_order_like):
        """確定処理2成功"""
        request = DummyRequest()
        exp_famiport_order = mock.Mock()
        create_famiport_order.return_value = exp_famiport_order
        plugin = self._makeOne()
        build_famiport_order_dict.return_value = {}
        build_ticket_dicts_from_order_like.return_value = [mock.Mock()]

        for order in self.orders:
            cart = order.cart
            lookup_famiport_tenant.return_value = self.famiport_tenant
            exp_call_args = mock.call(request, cart, plugin=plugin)
            plugin.finish2(request, cart)
            self.assertEqual(create_famiport_order.call_args, exp_call_args)

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

    @mock.patch('altair.app.ticketing.payments.plugins.famiport.order_models.Order.create_from_cart')
    @mock.patch('altair.app.ticketing.payments.plugins.famiport.create_famiport_order')
    def test_finish(self, create_famiport_order, create_from_cart):
        """確定処理成功"""
        create_famiport_order.return_value = mock.Mock()
        request = DummyRequest()
        cart = self.orders[0].cart
        plugin = self._makeOne()

        res = plugin.finish(request, cart)
        self.assertEqual(res, None)

    @mock.patch('altair.app.ticketing.payments.plugins.famiport.build_ticket_dicts_from_order_like')
    @mock.patch('altair.app.ticketing.payments.plugins.famiport.build_famiport_order_dict')
    @mock.patch('altair.app.ticketing.payments.plugins.famiport.lookup_famiport_tenant')
    @mock.patch('altair.app.ticketing.payments.plugins.famiport.create_famiport_order')
    def test_finish2_success(self, create_famiport_order, lookup_famiport_tenant,
                             build_famiport_order_dict, build_ticket_dicts_from_order_like):
        """確定処理2成功"""
        request = DummyRequest()
        exp_famiport_order = mock.Mock()
        create_famiport_order.return_value = exp_famiport_order
        plugin = self._makeOne()
        build_famiport_order_dict.return_value = {}
        build_ticket_dicts_from_order_like.return_value = [mock.Mock()]
        lookup_famiport_tenant.return_value = self.famiport_tenant

        for order in self.orders:
            cart = order.cart
            exp_call_args = mock.call(request, cart, plugin=plugin)
            plugin.finish2(request, cart)
            self.assertEqual(create_famiport_order.call_args, exp_call_args)

        # request = DummyRequest()
        # plugin = self._makeOne()
        # for order in self.orders:
        #     famiport_order = self._callFUT(plugin.finish2, request, order.cart)
        #     self.assert_valid_famiport_order(famiport_order, order, plugin)

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

    @mock.patch('altair.app.ticketing.payments.plugins.famiport.build_ticket_dicts_from_order_like')
    @mock.patch('altair.app.ticketing.payments.plugins.famiport.build_famiport_order_dict')
    @mock.patch('altair.app.ticketing.payments.plugins.famiport.lookup_famiport_tenant')
    @mock.patch('altair.app.ticketing.payments.plugins.famiport.order_models.Order.create_from_cart')
    @mock.patch('altair.app.ticketing.payments.plugins.famiport.create_famiport_order')
    def test_finish(self, create_famiport_order, create_from_cart, lookup_famiport_tenant,
                    build_famiport_order_dict, build_ticket_dicts_from_order_like):
        """確定処理成功"""
        exp_order = create_from_cart.return_value = mock.Mock(total_amount=100)
        create_famiport_order.return_value = mock.Mock()
        request = DummyRequest()
        cart = self.orders[0].cart
        plugin = self._makeOne()
        build_famiport_order_dict.return_value = {}
        build_ticket_dicts_from_order_like.return_value = [mock.Mock()]
        lookup_famiport_tenant.return_value = self.famiport_tenant
        order = plugin.finish(request, cart)

        self.assertEqual(order, exp_order)
        self.assertTrue(create_famiport_order.called)

    @mock.patch('altair.app.ticketing.payments.plugins.famiport.build_ticket_dicts_from_order_like')
    @mock.patch('altair.app.ticketing.payments.plugins.famiport.build_famiport_order_dict')
    @mock.patch('altair.app.ticketing.payments.plugins.famiport.lookup_famiport_tenant')
    @mock.patch('altair.app.ticketing.payments.plugins.famiport.create_famiport_order')
    def test_finish2_success(self, create_famiport_order, lookup_famiport_tenant,
                             build_famiport_order_dict, build_ticket_dicts_from_order_like):
        """確定処理2成功"""
        request = DummyRequest()
        exp_famiport_order = mock.Mock()
        create_famiport_order.return_value = exp_famiport_order
        plugin = self._makeOne()

        build_famiport_order_dict.return_value = {}
        build_ticket_dicts_from_order_like.return_value = [mock.Mock()]
        lookup_famiport_tenant.return_value = self.famiport_tenant
        for order in self.orders:
            cart = order.cart
            exp_call_args = mock.call(request, cart, plugin=plugin)
            plugin.finish2(request, cart)
            self.assertEqual(create_famiport_order.call_args, exp_call_args)

        # request = DummyRequest()
        # plugin = self._makeOne()
        # for order in self.orders:
        #     famiport_order = self._callFUT(plugin.finish2, request, order.cart)
        #     self.assert_valid_famiport_order(famiport_order, order, plugin)

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


class FamiPortViewletTest(TestCase):
    def _target(self):
        from .famiport import FamiPortPaymentDeliveryPlugin
        return FamiPortPaymentDeliveryPlugin

    def _callFUT(self, *args, **kwds):
        func = self._target()
        return func(*args, **kwds)


class FamiPortPaymentViewletTest(FamiPortViewletTest):
    def setUp(self):
        self.name = u'ファミポート'
        self.description = u'説明説明説明説明説明'
        self.notice = u'日本語日本語日本語日本語'
        self.payment_method = DummyModel(
            name=self.name,
            description=self.description,
            )
        self.payment_delivery_pair = DummyModel(payment_method=self.payment_method)
        self.order = DummyModel(
            order_no='XX000001234',
            payment_delivery_pair=self.payment_delivery_pair,
            )
        self.cart = DummyModel(payment_delivery_pair=self.payment_delivery_pair)
        self.context = DummyResource(
            order=self.order,
            order_no=self.order.order_no,
            cart=self.cart,
            description=self.payment_method.description,
            mail_data=mock.Mock(return_value=self.notice),
            )
        self.request = DummyRequest()

    def _target(self):
        from .famiport import payment_completion_viewlet as func
        return func


class FamiPortPaymentConfirmViewletTest(FamiPortPaymentViewletTest):
    def _target(self):
        from .famiport import reserved_number_payment_confirm_viewlet as func
        return func

    @mock.patch('altair.app.ticketing.payments.plugins.famiport.cart_helper')
    def test_it(self, cart_helper):
        res = self._callFUT(self.context, self.request)
        self.assertEqual(res, {
            'payment_name': self.name,
            'description': self.description,
            'h': cart_helper,
            })


class FamiPortPaymentCompletionViewletTest(FamiPortPaymentViewletTest):
    def _target(self):
        from .famiport import reserved_number_payment_viewlet as func
        return func

    @mock.patch('altair.app.ticketing.payments.plugins.famiport.lookup_famiport_tenant')
    @mock.patch('altair.app.ticketing.payments.plugins.famiport.cart_helper')
    @mock.patch('altair.app.ticketing.famiport.api.get_famiport_order')
    def test_it(self, get_famiport_order, cart_helper, lookup_famiport_tenant):
        exp_famiport_order = mock.Mock()
        get_famiport_order.return_value = exp_famiport_order
        lookup_famiport_tenant.return_value = mock.Mock()
        res = self._callFUT(self.context, self.request)
        self.assertEqual(res, {
            'payment_name': self.name,
            'description': self.description,
            'famiport_order': exp_famiport_order,
            'h': cart_helper,
            })


class FamiPortPaymentCompletionMailViewletTest(FamiPortPaymentViewletTest):
    def _target(self):
        from .famiport import payment_mail_viewlet as func
        return func

    @mock.patch('altair.app.ticketing.famiport.api.get_famiport_order')
    @mock.patch('altair.app.ticketing.payments.plugins.famiport.lookup_famiport_tenant')
    @mock.patch('altair.app.ticketing.payments.plugins.famiport.cart_helper')
    def test_it(self, cart_helper, lookup_famiport_tenant, get_famiport_order):
        lookup_famiport_tenant.return_value = mock.Mock()
        res = self._callFUT(self.context, self.request)
        for key, value in {'description': self.description, 'h': cart_helper}.items():
            self.assertEqual(value, res.get(key), 'invalid value: key={}, exp_value={} != {}'.format(
                key, repr(value), repr(res.get(key))))


class FamiPortPaymentCancelMailViewletTest(FamiPortPaymentViewletTest):
    def _target(self):
        from .famiport import cancel_mail as func
        return func

    def test_it(self):
        res = self._callFUT(self.context, self.request)
        self.assertEqual(res.text, self.notice)


class FamiPortPaymentNoticeViewletTest(FamiPortPaymentViewletTest):
    def _target(self):
        from .famiport import lot_payment_notice_viewlet as func
        return func

    def test_it(self):
        res = self._callFUT(self.context, self.request)
        self.assertEqual(res.text, self.notice)


class FamiPortDeliveryViewletTest(FamiPortViewletTest):
    def setUp(self):
        self.name = u'ファミポート'
        self.description = u'説明説明説明説明説明'
        self.notice = u'日本語日本語日本語日本語'
        self.delivery_method = DummyModel(
            name=self.name,
            description=self.description,
            )
        self.payment_delivery_pair = DummyModel(delivery_method=self.delivery_method)
        self.order = DummyModel(
            order_no='XX000001234',
            payment_delivery_pair=self.payment_delivery_pair,
            )
        self.cart = DummyModel(payment_delivery_pair=self.payment_delivery_pair)
        self.context = DummyResource(
            order=self.order,
            order_no=self.order.order_no,
            cart=self.cart,
            description=self.delivery_method.description,
            mail_data=mock.Mock(return_value=self.notice),
            )
        self.request = DummyRequest()

    def _target(self):
        from .famiport import deliver_completion_viewlet as func
        return func


class FamiPortDeliveryConfirmViewletTest(FamiPortDeliveryViewletTest):
    def _target(self):
        from .famiport import deliver_confirm_viewlet as func
        return func

    @mock.patch('altair.app.ticketing.payments.plugins.famiport.cart_helper')
    def test_it(self, cart_helper):
        res = self._callFUT(self.context, self.request)
        self.assertEqual(res, {
            'delivery_name': self.name,
            'description': self.description,
            'h': cart_helper,
            })


class FamiPortDeliveryCompletionViewletTest(FamiPortDeliveryViewletTest):
    def _target(self):
        from .famiport import deliver_completion_viewlet as func
        return func

    @mock.patch('altair.app.ticketing.payments.plugins.famiport.cart_helper')
    @mock.patch('altair.app.ticketing.famiport.api.get_famiport_order')
    def test_it(self, get_famiport_order, cart_helper):
        exp_famiport_order = mock.Mock()
        get_famiport_order.return_value = exp_famiport_order
        res = self._callFUT(self.context, self.request)
        self.assertEqual(res, {
            'delivery_name': self.name,
            'description': self.description,
            'famiport_order': exp_famiport_order,
            'h': cart_helper,
            })


class FamiPortDeliveryCompletionMailViewletTest(FamiPortDeliveryViewletTest):
    def _target(self):
        from .famiport import deliver_completion_mail_viewlet as func
        return func

    @mock.patch('altair.app.ticketing.payments.plugins.famiport.cart_helper')
    def test_it(self, cart_helper):
        res = self._callFUT(self.context, self.request)
        self.assertEqual(res, {
            'notice': self.notice,
            'h': cart_helper,
            })


class FamiPortDeliveryNoticeViewletTest(FamiPortDeliveryViewletTest):
    def _target(self):
        from .famiport import delivery_notice_viewlet as func
        return func

    @mock.patch('altair.app.ticketing.payments.plugins.famiport.cart_helper')
    def test_it(self, cart_helper):
        res = self._callFUT(self.context, self.request)
        self.assertEqual(res.text, u'ファミポート受け取り')


class CreateFamiPortOrderTest(TestCase):
    def _get_target(self):
        from altair.app.ticketing.payments.plugins.famiport import create_famiport_order as target
        return target

    @mock.patch('altair.app.ticketing.payments.plugins.famiport.select_famiport_order_type')
    @mock.patch('altair.app.ticketing.payments.plugins.famiport.lookup_famiport_tenant')
    @mock.patch('altair.app.ticketing.payments.plugins.famiport.famiport_api.create_famiport_order')
    @mock.patch('altair.app.ticketing.payments.plugins.famiport.build_ticket_dicts_from_order_like')
    @mock.patch('altair.app.ticketing.payments.plugins.famiport.get_altair_famiport_sales_segment_pair')
    @mock.patch('altair.app.ticketing.payments.plugins.famiport.famiport_api.get_famiport_sales_segment_by_userside_id')
    def test_it(self, get_famiport_sales_segment_by_userside_id, get_altair_famiport_sales_segment_pair,
                build_ticket_dicts_from_order_like, create_famiport_order, lookup_famiport_tenant,
                select_famiport_order_type):
        from altair.app.ticketing.famiport.models import FamiPortOrderType
        select_famiport_order_type.return_value = FamiPortOrderType.Ticketing.value
        tenant = mock.Mock(code='XX')
        lookup_famiport_tenant.return_value = tenant
        famiport_sales_segment = mock.MagicMock(
            event_code_1='EVENT_CODE_1',
            EVENT_code_2='EVENT_CODE_2',
            performance_code='PERFORMANCE_CODE',
            sales_segment_code='CODE',
            )
        get_famiport_sales_segment_by_userside_id.return_value = famiport_sales_segment

        famiport_tickets = mock.Mock()
        build_ticket_dicts_from_order_like.return_value = famiport_tickets
        request = DummyRequest()
        cart = DummyModel(
            organization_id=1,
            total_amount=100,
            transaction_fee=1,
            delivery_fee=1,
            system_fee=1,
            special_fee=1,
            order_no=u'XX000001234',
            payment_start_at=None,
            payment_due_at=None,
            issuing_start_at=None,
            issuing_end_at=None,
            shipping_address=DummyModel(
                prefecture=u'東京都',
                city=u'品川区',
                address_1=u'西五反田',
                address_2=u'aaa',
                tel_1='07011112222',
                email_1='dev@ticketstar.jp',
                last_name=u'楽天',
                first_name=u'太郎',
                ),
            sales_segment=DummyModel(
                id=1,
                ),
            )
        in_payment = True
        plugin = mock.Mock()
        target = self._get_target()
        famiport_order = target(request, cart, plugin, in_payment)
        order_like = cart
        customer_address_1 = order_like.shipping_address.prefecture + order_like.shipping_address.city + order_like.shipping_address.address_1
        customer_address_2 = order_like.shipping_address.address_2
        customer_name = order_like.shipping_address.last_name + order_like.shipping_address.first_name

        total_amount = cart.total_amount
        system_fee = order_like.transaction_fee + order_like.system_fee + order_like.special_fee
        ticketing_fee = cart.delivery_fee
        ticket_payment = order_like.total_amount - (order_like.system_fee + order_like.transaction_fee + order_like.delivery_fee + order_like.special_fee)
        customer_phone_number = (order_like.shipping_address.tel_1 or order_like.shipping_address.tel_2 or u'').replace(u'-', u'')

        exp_call_args = mock.call(
            request,
            client_code=tenant.code,
            type_=FamiPortOrderType.Ticketing.value,
            order_no=order_like.order_no,
            event_code_1=famiport_sales_segment['event_code_1'],
            event_code_2=famiport_sales_segment['event_code_2'],
            performance_code=famiport_sales_segment['performance_code'],
            sales_segment_code=famiport_sales_segment['code'],
            customer_address_1=customer_address_1,
            customer_address_2=customer_address_2,
            customer_name=customer_name,
            customer_phone_number=customer_phone_number,
            total_amount=0, # total_amount,
            system_fee=0, # system_fee,
            ticketing_fee=0, # ticketing_fee,
            ticket_payment=0, # ticket_payment,
            tickets=build_ticket_dicts_from_order_like(request, order_like),
            payment_start_at=order_like.payment_start_at,
            payment_due_at=order_like.payment_due_at,
            ticketing_start_at=order_like.issuing_start_at,
            ticketing_end_at=order_like.issuing_end_at,
            payment_sheet_text=None,
            )
        attrs = [
                'client_code',
                'type_',
                'order_no',
                'event_code_1',
                'event_code_2',
                'performance_code',
                'sales_segment_code',
                'customer_address_1',
                'customer_address_2',
                'customer_name',
                'customer_phone_number',
                'total_amount',
                'system_fee',
                'ticketing_fee',
                'ticket_payment',
                'tickets',
                'payment_start_at',
                'payment_due_at',
                'ticketing_start_at',
                'ticketing_end_at',
                'payment_sheet_text',
                ]

        for attr in attrs:
            val = create_famiport_order.call_args[1][attr]
            exp = exp_call_args[2][attr]
            self.assertEqual(val, exp, u'error {}: {} != {}'.format(
                attr, val, exp,
                ))

        self.assertTrue(famiport_order)


class SelectFamiportOrderTypeTest(TestCase):
    def _get_target(self):
        from .famiport import select_famiport_order_type as func
        return func

    def _callFUT(self, *args, **kwds):
        target = self._get_target()
        return target(*args, **kwds)

    def test_it(self):
        """ファミポート決済の場合は前払"""
        from altair.app.ticketing.famiport.models import FamiPortOrderType
        from .famiport import FamiPortPaymentPlugin as PluginClass
        exp_type = FamiPortOrderType.PaymentOnly.value
        payment_start_at = None
        issuing_start_at = None

        order_like = mock.Mock(
            payment_start_at=payment_start_at,
            issuing_start_at=issuing_start_at,
            )
        plugin = PluginClass()
        args = [
            order_like,
            plugin,
            ]
        kwds = {}
        res = self._callFUT(*args, **kwds)
        self.assertEqual(res, exp_type)

    def test_payment_plugin(self):
        """ファミポート決済の場合は前払"""
        from altair.app.ticketing.famiport.models import FamiPortOrderType
        from .famiport import FamiPortPaymentPlugin as PluginClass
        exp_type = FamiPortOrderType.PaymentOnly.value
        payment_start_at = None
        issuing_start_at = None

        order_like = mock.Mock(
            payment_start_at=payment_start_at,
            issuing_start_at=issuing_start_at,
            )
        plugin = PluginClass()
        args = []
        kwds = {
            'order_like': order_like,
            'plugin': plugin
             }
        res = self._callFUT(*args, **kwds)
        self.assertEqual(res, exp_type)

    def test_delivery_plugin(self):
        """ファミポート引き取りの場合は代済"""
        from altair.app.ticketing.famiport.models import FamiPortOrderType
        from .famiport import FamiPortDeliveryPlugin as PluginClass
        exp_type = FamiPortOrderType.Ticketing.value
        payment_start_at = None
        issuing_start_at = None

        order_like = mock.Mock(
            payment_start_at=payment_start_at,
            issuing_start_at=issuing_start_at,
            )
        plugin = PluginClass()
        args = []
        kwds = {
            'order_like': order_like,
            'plugin': plugin
             }
        res = self._callFUT(*args, **kwds)
        self.assertEqual(res, exp_type)

    def test_payment_delivery_plugin_normal(self):
        """ファミポート決済/ファミポート引き取で支払期限も発券開始日時も指定されていない場合は代引"""
        from altair.app.ticketing.famiport.models import FamiPortOrderType
        from .famiport import FamiPortPaymentDeliveryPlugin as PluginClass
        exp_type = FamiPortOrderType.CashOnDelivery.value
        payment_start_at = None
        issuing_start_at = None

        order_like = mock.Mock(
            payment_start_at=payment_start_at,
            issuing_start_at=issuing_start_at,
            )
        plugin = PluginClass()
        args = []
        kwds = {
            'order_like': order_like,
            'plugin': plugin
             }
        res = self._callFUT(*args, **kwds)
        self.assertEqual(res, exp_type)

    def test_payment_delivery_plugin_payment_start_at(self):
        """ファミポート決済/ファミポート引き取で支払期限のみ指定されている場合は代引"""
        from datetime import datetime
        from altair.app.ticketing.famiport.models import FamiPortOrderType
        from .famiport import FamiPortPaymentDeliveryPlugin as PluginClass
        exp_type = FamiPortOrderType.CashOnDelivery.value
        _now = datetime.now()
        payment_start_at = _now
        issuing_start_at = None

        order_like = mock.Mock(
            payment_start_at=payment_start_at,
            issuing_start_at=issuing_start_at,
            )
        plugin = PluginClass()
        args = []
        kwds = {
            'order_like': order_like,
            'plugin': plugin
             }
        res = self._callFUT(*args, **kwds)
        self.assertEqual(res, exp_type)

    def test_payment_delivery_plugin_issuing_start_at(self):
        """ファミポート決済/ファミポート引き取で発券開始日時のみ指定されている場合は代引"""
        from datetime import datetime
        from altair.app.ticketing.famiport.models import FamiPortOrderType
        from .famiport import FamiPortPaymentDeliveryPlugin as PluginClass
        exp_type = FamiPortOrderType.CashOnDelivery.value
        _now = datetime.now()
        payment_start_at = None
        issuing_start_at = _now

        order_like = mock.Mock(
            payment_start_at=payment_start_at,
            issuing_start_at=issuing_start_at,
            )
        plugin = PluginClass()
        args = []
        kwds = {
            'order_like': order_like,
            'plugin': plugin
             }
        res = self._callFUT(*args, **kwds)
        self.assertEqual(res, exp_type)

    def test_payment_delivery_plugin_later_ticketing(self):
        """ファミポート決済/ファミポート引き取で支払期限が発券開始日時よりも前の場合は前払後日前払"""
        from datetime import datetime, timedelta
        from altair.app.ticketing.famiport.models import FamiPortOrderType
        from .famiport import FamiPortPaymentDeliveryPlugin as PluginClass
        exp_type = FamiPortOrderType.Payment.value
        _now = datetime.now()
        payment_start_at = _now
        issuing_start_at = _now + timedelta(seconds=1)

        order_like = mock.Mock(
            payment_start_at=payment_start_at,
            issuing_start_at=issuing_start_at,
            )
        plugin = PluginClass()
        args = []
        kwds = {
            'order_like': order_like,
            'plugin': plugin
             }
        res = self._callFUT(*args, **kwds)
        self.assertEqual(res, exp_type)
