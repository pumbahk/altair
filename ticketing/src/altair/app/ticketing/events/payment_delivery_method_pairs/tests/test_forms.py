# coding=utf-8
import inspect

from mock import patch
from unittest import TestCase

from altair.app.ticketing.payments.plugins import (
    MULTICHECKOUT_PAYMENT_PLUGIN_ID,
    CHECKOUT_PAYMENT_PLUGIN_ID,
    SEJ_PAYMENT_PLUGIN_ID,
    RESERVE_NUMBER_PAYMENT_PLUGIN_ID,
    FREE_PAYMENT_PLUGIN_ID,
    FAMIPORT_PAYMENT_PLUGIN_ID,
    SHIPPING_DELIVERY_PLUGIN_ID,
    SEJ_DELIVERY_PLUGIN_ID,
    RESERVE_NUMBER_DELIVERY_PLUGIN_ID,
    QR_DELIVERY_PLUGIN_ID,
    ORION_DELIVERY_PLUGIN_ID,
    FAMIPORT_DELIVERY_PLUGIN_ID,
    QR_AES_DELIVERY_PLUGIN_ID,
    WEB_COUPON_DELIVERY_PLUGIN_ID
)
from altair.app.ticketing.core.models import PaymentMethod, DeliveryMethod, DateCalculationBase, \
    PaymentDeliveryMethodPair
from altair.app.ticketing.events.payment_delivery_method_pairs.forms import PaymentDeliveryMethodPairForm


class PaymentDeliveryMethodPairFormTest(TestCase):
    # 選択不可期間のデフォルト値
    UNAVAILABLE_PERIOD_DAYS = {
        # 決済方法：コンビニ　引取方法：コンビニ
        (SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID): dict(unavailable_period_days=4),
        (FAMIPORT_PAYMENT_PLUGIN_ID, FAMIPORT_DELIVERY_PLUGIN_ID): dict(unavailable_period_days=4),
        # 決済方法：コンビニ　引取方法：QRコード
        (SEJ_PAYMENT_PLUGIN_ID, QR_DELIVERY_PLUGIN_ID): dict(unavailable_period_days=4),
        (FAMIPORT_PAYMENT_PLUGIN_ID, QR_DELIVERY_PLUGIN_ID): dict(unavailable_period_days=4),
        (SEJ_PAYMENT_PLUGIN_ID, QR_AES_DELIVERY_PLUGIN_ID): dict(unavailable_period_days=4),
        (FAMIPORT_PAYMENT_PLUGIN_ID, QR_AES_DELIVERY_PLUGIN_ID): dict(unavailable_period_days=4),
        # 決済方法：コンビニ　引取方法：イベントゲート
        (SEJ_PAYMENT_PLUGIN_ID, ORION_DELIVERY_PLUGIN_ID): dict(unavailable_period_days=4),
        (FAMIPORT_PAYMENT_PLUGIN_ID, ORION_DELIVERY_PLUGIN_ID): dict(unavailable_period_days=4),
        # 決済方法：コンビニ　引取方法：窓口
        (SEJ_PAYMENT_PLUGIN_ID, RESERVE_NUMBER_DELIVERY_PLUGIN_ID): dict(unavailable_period_days=4),
        (FAMIPORT_PAYMENT_PLUGIN_ID, RESERVE_NUMBER_DELIVERY_PLUGIN_ID): dict(unavailable_period_days=4),
        # 決済方法：コンビニ　引取方法：WEBクーポン
        (SEJ_PAYMENT_PLUGIN_ID, WEB_COUPON_DELIVERY_PLUGIN_ID): dict(unavailable_period_days=4),
        (FAMIPORT_PAYMENT_PLUGIN_ID, WEB_COUPON_DELIVERY_PLUGIN_ID): dict(unavailable_period_days=4),
        # 決済方法：窓口・無料　引取方法：コンビニ
        (RESERVE_NUMBER_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID): dict(unavailable_period_days=4),
        (RESERVE_NUMBER_PAYMENT_PLUGIN_ID, FAMIPORT_DELIVERY_PLUGIN_ID): dict(unavailable_period_days=4),
        (FREE_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID): dict(unavailable_period_days=4),
        (FREE_PAYMENT_PLUGIN_ID, FAMIPORT_DELIVERY_PLUGIN_ID): dict(unavailable_period_days=4),
        # 決済方法：クレジットカード　引取方法：配送
        (MULTICHECKOUT_PAYMENT_PLUGIN_ID, SHIPPING_DELIVERY_PLUGIN_ID): dict(unavailable_period_days=14),
        # 決済方法：楽天ペイ　引取方法：配送
        (CHECKOUT_PAYMENT_PLUGIN_ID, SHIPPING_DELIVERY_PLUGIN_ID): dict(unavailable_period_days=14),
        # 決済方法：窓口・無料　引取方法：配送
        (RESERVE_NUMBER_PAYMENT_PLUGIN_ID, SHIPPING_DELIVERY_PLUGIN_ID): dict(unavailable_period_days=14),
        (FREE_PAYMENT_PLUGIN_ID, SHIPPING_DELIVERY_PLUGIN_ID): dict(unavailable_period_days=14),
        # 決済方法：コンビニ　引取方法：配送
        (SEJ_PAYMENT_PLUGIN_ID, SHIPPING_DELIVERY_PLUGIN_ID): dict(unavailable_period_days=17),
        (FAMIPORT_PAYMENT_PLUGIN_ID, SHIPPING_DELIVERY_PLUGIN_ID): dict(unavailable_period_days=17),
    }
    # コンビニ発券開始日時のデフォルト値
    ISSUING_INTERVAL_DATE_TIMES = {
        # 決済方法：楽天ペイ・クレジットカード
        # 引取方法：コンビニ・QRコード・イベントゲート
        (payment_plugin_id, delivery_plugin_id):
            dict(
                issuing_interval_days_selected_choice=DateCalculationBase.OrderDateTime.v,
                issuing_interval_days=1,
                issuing_interval_time_readonly=True
            ) for delivery_plugin_id in [SEJ_DELIVERY_PLUGIN_ID, FAMIPORT_DELIVERY_PLUGIN_ID,
                                         QR_DELIVERY_PLUGIN_ID, QR_AES_DELIVERY_PLUGIN_ID,
                                         ORION_DELIVERY_PLUGIN_ID]
        for payment_plugin_id in [CHECKOUT_PAYMENT_PLUGIN_ID, MULTICHECKOUT_PAYMENT_PLUGIN_ID]
    }
    # コンビニ発券期限日時のデフォルト値
    ISSUING_END_IN_DATE_TIMES = {
        (payment_plugin_id, delivery_plugin_id):
            dict(
                issuing_end_in_days_selected_choice=DateCalculationBase.PerformanceEndDate.v,
                issuing_end_in_days=30,
            ) for payment_plugin_id, delivery_plugin_id in [
            # 決済方法：コンビニ　引取方法：コンビニ
            (SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID),
            (FAMIPORT_PAYMENT_PLUGIN_ID, FAMIPORT_DELIVERY_PLUGIN_ID),
            # 決済方法：コンビニ　引取方法：QRコード
            (SEJ_PAYMENT_PLUGIN_ID, QR_DELIVERY_PLUGIN_ID),
            (FAMIPORT_PAYMENT_PLUGIN_ID, QR_DELIVERY_PLUGIN_ID),
            (SEJ_PAYMENT_PLUGIN_ID, QR_AES_DELIVERY_PLUGIN_ID),
            (FAMIPORT_PAYMENT_PLUGIN_ID, QR_AES_DELIVERY_PLUGIN_ID),
            # 決済方法：コンビニ　引取方法：イベントゲート
            (SEJ_PAYMENT_PLUGIN_ID, ORION_DELIVERY_PLUGIN_ID),
            (FAMIPORT_PAYMENT_PLUGIN_ID, ORION_DELIVERY_PLUGIN_ID),
            # 決済方法：クレジットカード　引取方法：コンビニ
            (MULTICHECKOUT_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID),
            (MULTICHECKOUT_PAYMENT_PLUGIN_ID, FAMIPORT_DELIVERY_PLUGIN_ID),
            # 決済方法：楽天ペイ　引取方法：コンビニ
            (CHECKOUT_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID),
            (CHECKOUT_PAYMENT_PLUGIN_ID, FAMIPORT_DELIVERY_PLUGIN_ID),
            # 決済方法：クレジットカード　引取方法：QRコード
            (MULTICHECKOUT_PAYMENT_PLUGIN_ID, QR_DELIVERY_PLUGIN_ID),
            (MULTICHECKOUT_PAYMENT_PLUGIN_ID, QR_AES_DELIVERY_PLUGIN_ID),
            # 決済方法：楽天ペイ　引取方法：QRコード
            (CHECKOUT_PAYMENT_PLUGIN_ID, QR_DELIVERY_PLUGIN_ID),
            (CHECKOUT_PAYMENT_PLUGIN_ID, QR_AES_DELIVERY_PLUGIN_ID),
            # 決済方法：クレジットカード　引取方法：イベントゲート
            (MULTICHECKOUT_PAYMENT_PLUGIN_ID, ORION_DELIVERY_PLUGIN_ID),
            (MULTICHECKOUT_PAYMENT_PLUGIN_ID, ORION_DELIVERY_PLUGIN_ID),
            # 決済方法：楽天ペイ　引取方法：イベントゲート
            (CHECKOUT_PAYMENT_PLUGIN_ID, ORION_DELIVERY_PLUGIN_ID),
            (CHECKOUT_PAYMENT_PLUGIN_ID, ORION_DELIVERY_PLUGIN_ID),
            # 決済方法：窓口・無料　引取方法：コンビニ
            (RESERVE_NUMBER_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID),
            (RESERVE_NUMBER_PAYMENT_PLUGIN_ID, FAMIPORT_DELIVERY_PLUGIN_ID),
            (FREE_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID),
            (FREE_PAYMENT_PLUGIN_ID, FAMIPORT_DELIVERY_PLUGIN_ID),
            # 決済方法：窓口・無料　引取方法：QRコード
            (RESERVE_NUMBER_PAYMENT_PLUGIN_ID, QR_DELIVERY_PLUGIN_ID),
            (RESERVE_NUMBER_PAYMENT_PLUGIN_ID, QR_AES_DELIVERY_PLUGIN_ID),
            (FREE_PAYMENT_PLUGIN_ID, QR_DELIVERY_PLUGIN_ID),
            (FREE_PAYMENT_PLUGIN_ID, QR_AES_DELIVERY_PLUGIN_ID),
            # 決済方法：窓口・無料　引取方法：イベントゲート
            (RESERVE_NUMBER_PAYMENT_PLUGIN_ID, ORION_DELIVERY_PLUGIN_ID),
            (FREE_PAYMENT_PLUGIN_ID, ORION_DELIVERY_PLUGIN_ID),
        ]
    }

    def setUp(self):
        self.pdmp_form = PaymentDeliveryMethodPairForm()

    def _assert_defaults(self, payment_plugin_id, delivery_plugin_id, defaults):
        # ベースのデフォルト値
        expected = self.pdmp_form.basic_default_values(PaymentMethod(payment_plugin_id=payment_plugin_id),
                                                       DeliveryMethod(delivery_plugin_id=delivery_plugin_id))
        # 選択不可期間のデフォルト値を反映
        expected.update(self.UNAVAILABLE_PERIOD_DAYS.get((payment_plugin_id, delivery_plugin_id), {}))
        # コンビニ発券開始日時のデフォルト値を反映
        expected.update(self.ISSUING_INTERVAL_DATE_TIMES.get((payment_plugin_id, delivery_plugin_id), {}))
        # コンビニ発券期限日時のデフォルト値を反映
        expected.update(self.ISSUING_END_IN_DATE_TIMES.get((payment_plugin_id, delivery_plugin_id), {}))
        self.assertDictEqual(expected, defaults)

    @patch('{}.get_payment_delivery_methods'.format(inspect.getmodule(PaymentDeliveryMethodPairForm).__name__))
    def test_pdmp_default_values(self, mock_get_pdmp_methods):
        """支払・引取方法ごとの相対指定のデフォルト値をテスト"""
        # 決済方法一覧
        payment_plugin_ids = [
            # クレジットカード
            MULTICHECKOUT_PAYMENT_PLUGIN_ID,
            # 楽天PAY
            CHECKOUT_PAYMENT_PLUGIN_ID,
            # コンビニ
            SEJ_PAYMENT_PLUGIN_ID, FAMIPORT_PAYMENT_PLUGIN_ID,
            # 窓口
            RESERVE_NUMBER_PAYMENT_PLUGIN_ID,
            # 無料
            FREE_PAYMENT_PLUGIN_ID
        ]
        # 引取方法一覧
        delivery_plugin_ids = [
            # 配送
            SHIPPING_DELIVERY_PLUGIN_ID,
            # コンビニ
            SEJ_DELIVERY_PLUGIN_ID, FAMIPORT_DELIVERY_PLUGIN_ID,
            # 窓口
            RESERVE_NUMBER_DELIVERY_PLUGIN_ID,
            # QR
            QR_DELIVERY_PLUGIN_ID, QR_AES_DELIVERY_PLUGIN_ID,
            # イベントゲート
            ORION_DELIVERY_PLUGIN_ID,
            # WEBクーポン
            WEB_COUPON_DELIVERY_PLUGIN_ID,
        ]

        # 全ての支払方法と引取方法の組み合わせでテストします。
        for payment_plugin_id in payment_plugin_ids:
            for delivery_plugin_id in delivery_plugin_ids:
                # コンビニ違いの無効な組み合わせをスキップ
                if (payment_plugin_id, delivery_plugin_id) in PaymentDeliveryMethodPair.INVALID_PLUGIN_ID_PAIRS:
                    continue

                payment_method = PaymentMethod(payment_plugin_id=payment_plugin_id)
                delivery_method = DeliveryMethod(delivery_plugin_id=delivery_plugin_id)
                mock_get_pdmp_methods.return_value = payment_method, delivery_method
                # デフォルト値を取得
                defaults = self.pdmp_form.default_values_for_pdmp(payment_method.id, delivery_method.id)
                self._assert_defaults(payment_plugin_id, delivery_plugin_id, defaults)
