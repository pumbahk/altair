# -*- coding: utf-8 -*-
"""ファミポート決済/引取プラグイン
"""
from markupsafe import Markup
from zope.interface import implementer
from pyramid.response import Response

from altair.pyramid_dynamic_renderer import lbr_view_config
from altair.app.ticketing.cart.interfaces import (
    ICartPayment,
    ICartDelivery,
    )
from altair.app.ticketing.payments.interfaces import (
    IOrderPayment,
    IPaymentPlugin,
    IDeliveryPlugin,
    )
from altair.app.ticketing.mails.interfaces import (
    ICompleteMailResource,
    ILotsElectedMailResource,
    IOrderCancelMailResource,
    ILotsAcceptedMailResource,
    ILotsRejectedMailResource,
    )

import altair.app.ticketing.famiport.api as famiport_api
from altair.app.ticketing.famiport.exc import FamiPortError

from ..interfaces import IOrderDelivery
from ..exceptions import PaymentPluginException
import altair.app.ticketing.orders.models as order_models
from . import FAMIPORT_PAYMENT_PLUGIN_ID as PAYMENT_PLUGIN_ID
from . import FAMIPORT_DELIVERY_PLUGIN_ID as DELIVERY_PLUGIN_ID


def includeme(config):
    config.add_payment_plugin(FamiPortPaymentPlugin(), PAYMENT_PLUGIN_ID)
    config.add_delivery_plugin(FamiPortDeliveryPlugin(), DELIVERY_PLUGIN_ID)
    config.add_payment_delivery_plugin(FamiPortPaymentDeliveryPlugin(), PAYMENT_PLUGIN_ID, DELIVERY_PLUGIN_ID)
    config.scan(__name__)


class FamiPortPluginFailure(PaymentPluginException):
    pass


def refund_order(request, order, refund_record, now=None):
    """払い戻し"""
    raise FamiPortPluginFailure('unimplemented', None, None, None)


def cancel_order(request, order, now=None):
    """キャンセル"""
    raise FamiPortPluginFailure('unimplemented', None, None, None)


def refresh_order(request, order, now=None):
    """予約更新"""
    raise FamiPortPluginFailure('unimplemented', None, None, None)


def _overridable_payment(path, fallback_ua_type=None):
    """ここがどこに作用してくるのかわからない
    """
    from . import _template
    return _template(
        path, type='overridable', for_='payments', plugin_type='payment',
        plugin_id=PAYMENT_PLUGIN_ID, fallback_ua_type=fallback_ua_type,
        )


def _overridable_delivery(path, fallback_ua_type=None):
    from . import _template
    return _template(
        path, type='overridable', for_='payments', plugin_type='delivery',
        plugin_id=DELIVERY_PLUGIN_ID, fallback_ua_type=fallback_ua_type,
        )


@lbr_view_config(context=IOrderPayment, name='payment-%d' % PAYMENT_PLUGIN_ID,
                 renderer=_overridable_payment('famiport_payment_completion.html'))
def reserved_number_payment_viewlet(context, request):
    """決済方法の完了画面用のhtmlを生成"""
    payment_method = context.order.payment_delivery_pair.payment_method
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
class FamiPortPaymentPlugin(object):
    """ファミポート用決済プラグイン"""

    def validate_order(self, request, order_like):
        """予約を作成する前にvalidationする"""

    def prepare(self, request, cart):
        """前処理"""

    def finish(self, request, cart):
        """確定処理"""
        order = order_models.Order.create_from_cart(cart)
        cart.finish()
        self.finish2(request, cart)
        return order

    def finish2(self, request, cart):
        """確定処理2"""
        try:
            return famiport_api.create_famiport_order(request, cart)
        except FamiPortError:
            raise FamiPortPluginFailure()

    def finished(self, requrst, order):
        """支払状態遷移済みかどうかを判定"""
        return True

    def refresh(self, request, order):
        """決済側の状態をDBに反映"""
        return refresh_order(request, order)

    def cancel(self, request, order):
        """キャンセル処理"""
        return cancel_order(request, order)

    def refund(self, request, order, refund_record):
        """払戻処理"""
        return refund_order(request, order, refund_record)


@lbr_view_config(context=ICartDelivery, name='delivery-%d' % DELIVERY_PLUGIN_ID,
                 renderer=_overridable_delivery('famiport_delivery_confirm.html'))
def deliver_confirm_viewlet(context, request):
    """引取方法の確認画面のhtmlを生成"""
    cart = context.cart
    delivery_method = cart.payment_delivery_pair.delivery_method
    return dict(delivery_name=delivery_method.name, description=Markup(delivery_method.description))


@lbr_view_config(context=IOrderDelivery, name='delivery-%d' % DELIVERY_PLUGIN_ID,
                 renderer=_overridable_delivery('famiport_delivery_complete.html'))
def deliver_completion_viewlet(context, request):
    """引取方法の完了画面のhtmlを生成"""
    delivery_method = context.order.delivery_delivery_pair.delivery_method
    return dict(delivery_name=delivery_method.name, description=Markup(delivery_method.description))


@lbr_view_config(context=ICompleteMailResource, name='delivery-%d' % DELIVERY_PLUGIN_ID,
                 renderer=_overridable_delivery('famiport_mail_complete.html', fallback_ua_type='mail'))
def deliver_completion_mail_viewlet(context, request):
    """購入完了メールの配送方法部分のhtmlを出力する"""
    notice = context.mail_data("P", "notice")
    return dict(notice=notice)


@lbr_view_config(context=IOrderCancelMailResource, name='delivery-%d' % DELIVERY_PLUGIN_ID)
@lbr_view_config(context=ILotsRejectedMailResource, name='delivery-%d' % DELIVERY_PLUGIN_ID)
@lbr_view_config(context=ILotsAcceptedMailResource, name='delivery-%d' % DELIVERY_PLUGIN_ID)
@lbr_view_config(context=ILotsElectedMailResource, name='delivery-%d' % DELIVERY_PLUGIN_ID)
def delivery_notice_viewlet(context, request):
    return Response(text=u'ファミポート受け取り')


@implementer(IDeliveryPlugin)
class FamiPortDeliveryPlugin(object):
    def validate_order(self, request, order_like, update=False):
        """予約の検証"""

    def prepare(self, request, cart):
        """ 前処理 """

    def finish(self, request, cart):
        """確定時処理"""
        self.finish2(request, cart)

    def finish2(self, request, order_like):
        """確定時処理"""
        try:
            return famiport_api.create_famiport_order(request, order_like)  # noqa
        except FamiPortError:
            raise FamiPortPluginFailure()

    def finished(self, request, order):
        """ tokenが存在すること """
        return True

    def refresh(self, request, order):
        """リフレッシュ"""
        return refresh_order(request, order)

    def cancel(self, request, order):
        """キャンセル処理"""
        return cancel_order(request, order)

    def refund(self, request, order, refund_record):
        """払い戻し"""
        return refund_order(request, order, refund_record)


@implementer(IDeliveryPlugin)
class FamiPortPaymentDeliveryPlugin(object):
    def validate_order(self, request, order_like, update=False):
        """予約の検証"""

    def prepare(self, request, cart):
        """ 前処理 """

    def finish(self, request, cart):
        """ 確定時処理 """
        order = order_models.Order.create_from_cart(cart)
        cart.finish()
        self.finish2(request, cart)
        return order

    def finish2(self, request, order_like):
        """ 確定時処理 """
        try:
            return famiport_api.create_famiport_order(request, order_like)  # noqa
        except FamiPortError:
            raise FamiPortPluginFailure()

    def finished(self, request, order):
        """ tokenが存在すること """
        return True

    def refresh(self, request, order):
        """リフレッシュ"""
        return refresh_order(request, order)

    def cancel(self, request, order):
        """キャンセル処理"""
        return cancel_order(request, order)

    def refund(self, request, order, refund_record):
        """払い戻し"""
        return refund_order(request, order, refund_record)
