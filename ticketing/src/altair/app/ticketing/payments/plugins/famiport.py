# -*- coding: utf-8 -*-
from markupsafe import Markup
from zope.interface import implementer
from pyramid.response import Response

from altair.pyramid_dynamic_renderer import lbr_view_config
from altair.app.ticketing.cart.interfaces import ICartPayment
from altair.app.ticketing.payments.interfaces import (
    IPaymentPlugin,
    IOrderPayment,
    )
from altair.app.ticketing.mails.interfaces import (
    ICompleteMailResource,
    IOrderCancelMailResource,
    ILotsAcceptedMailResource,
    ILotsElectedMailResource,
    ILotsRejectedMailResource,
    )

from . import FAMIPORT_PAYMENT_PLUGIN_ID as PAYMENT_PLUGIN_ID


def includeme(config):
    config.add_payment_plugin(FamiportPaymentPlugin(), PAYMENT_PLUGIN_ID)
    config.scan(__name__)


def _overridable_payment(path, fallback_ua_type=None):
    """ここがどこに作用してくるのかわからない
    """
    from . import _template  # ??? ここは一体何がimportできるんだろう
    return _template(
        path, type='overridable', for_='payments', plugin_type='payment',
        plugin_id=PAYMENT_PLUGIN_ID, fallback_ua_type=fallback_ua_type,
        )


@lbr_view_config(context=IOrderPayment, name='payment-%d' % PAYMENT_PLUGIN_ID,
                 renderer=_overridable_payment('famiport_payment_completion.html'))
def reserved_number_payment_viewlet(context, request):
    """決済方法の完了画面用のhtmlを生成"""
    cart = context.cart
    payment_method = cart.payment_delivery_pair.payment_method
    return dict(payment_name=payment_method.name, description=Markup(payment_method.description))


@lbr_view_config(context=ICartPayment, name="payment-%d" % PAYMENT_PLUGIN_ID,
                 renderer=_overridable_payment("famiport_payment_confirm.html"))
def reserved_number_payment_confirm_viewlet(context, request):
    """決済方法の確認画面用のhtmlを生成"""
    cart = context.cart
    payment_method = cart.payment_delivery_pair.payment_method
    return dict(payment_name=payment_method.name, description=Markup(payment_method.description))


@lbr_view_config(context=ICompleteMailResource, name="payment-%d" % PAYMENT_PLUGIN_ID,
                 renderer=_overridable_payment("famiport_mail_complete.html", fallback_ua_type='mail'))
def complete_mail(context, request):
    """購入完了メールの決済方法部分のhtmlを出力する"""
    notice = context.mail_data("P", "notice")
    return dict(notice=notice)


@lbr_view_config(context=IOrderCancelMailResource, name="payment-%d" % PAYMENT_PLUGIN_ID)
def cancel_mail(context, request):
    """キャンセルメールの決済方法"""
    return Response(context.mail_data("P", "notice"))


@lbr_view_config(context=ILotsElectedMailResource, name="payment-%d" % PAYMENT_PLUGIN_ID)
@lbr_view_config(context=ILotsRejectedMailResource, name="payment-%d" % PAYMENT_PLUGIN_ID)
@lbr_view_config(context=ILotsAcceptedMailResource, name="payment-%d" % PAYMENT_PLUGIN_ID)
def lot_payment_notice_viewlet(context, request):
    return Response(context.mail_data("P", "notice"))


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
