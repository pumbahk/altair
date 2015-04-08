# -*- coding: utf-8 -*-
from zope.interface import implementer
from altair.app.ticketing.payments.interfaces import (
    IPaymentPlugin,
    )
from . import FAMIPORT_PAYMENT_PLUGIN_ID as PAYMENT_PLUGIN_ID


def includeme(config):
    config.add_payment_plugin(FamiportPaymentPlugin(), PAYMENT_PLUGIN_ID)
    config.scan(__name__)


@implementer(IPaymentPlugin)
class FamiportPaymentPlugin(object):
    """ファミポート用決済プラグイン"""

    def validate_order(self, request, order_like):
        """予約を作成する前にvalidationする"""

    def prepare(self, request, cart):
        """前処理"""

    def finish(self, request, cart):
        """確定処理"""

    def finish2(self, request, cart):
        """確定処理2"""

    def finished(self, requrst, order):
        """支払状態遷移済みかどうかを判定"""

    def refresh(self, request, order):
        """決済側の状態をDBに反映"""

    def cancel(self, request, order):
        """キャンセル処理"""

    def refund(self, request, order, refund_record):
        """払戻処理"""
