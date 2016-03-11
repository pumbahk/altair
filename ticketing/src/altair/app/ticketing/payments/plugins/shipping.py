# -*- coding:utf-8 -*-

from pyramid.view import view_config
from pyramid.response import Response
from zope.interface import implementer
from altair.pyramid_dynamic_renderer import lbr_view_config
from altair.app.ticketing.payments.interfaces import IDeliveryPlugin, IOrderDelivery
from altair.app.ticketing.cart.interfaces import ICartDelivery
from altair.app.ticketing.mails.interfaces import (
    ICompleteMailResource,
    IOrderCancelMailResource,
    ILotsAcceptedMailResource,
    ILotsElectedMailResource,
    ILotsRejectedMailResource,
    )

from . import models as m
from . import logger
from altair.app.ticketing.cart import helpers as cart_helper
from altair.app.ticketing.core import models as c_models

from . import SHIPPING_DELIVERY_PLUGIN_ID as PLUGIN_ID

def _overridable(path, fallback_ua_type=None):
    from . import _template
    return _template(path, type='overridable', for_='payments', plugin_type='delivery', plugin_id=PLUGIN_ID, fallback_ua_type=fallback_ua_type)

def includeme(config):
    config.add_delivery_plugin(ShippingDeliveryPlugin(), PLUGIN_ID)
    config.scan(__name__)

@lbr_view_config(context=ICartDelivery, name="delivery-1", renderer=_overridable("shipping_confirm.html"))
def deliver_confirm_viewlet(context, request):
    logger.debug(u"郵送")
    cart = context.cart
    return dict(shipping_address=cart.shipping_address)

@lbr_view_config(context=IOrderDelivery, name="delivery-1", renderer=_overridable("shipping_complete.html"))
def deliver_completion_viewlet(context, request):
    logger.debug(u"郵送")
    order = context.order
    return dict(shipping_address=order.shipping_address, order=order)

class ShippingDeliveryPlugin(object):
    def validate_order(self, request, order_like, update=False):
        """ なにかしたほうが良い?"""

    def validate_order_cancellation(self, request, order, now):
        """ キャンセルバリデーション """
        pass

    def prepare(self, request, cart):
        """ 前処理なし """

    def finish(self, request, cart):
        """ 確定処理なし """

    def finish2(self, request, order_like):
        """ 確定処理なし """

    def finished(self, request, order):
        """ shipping addressがあればOK?"""
        return bool(order.shipping_address)

    def refresh(self, request, order):
        if order.delivered_at is not None:
            raise Exception('order %s is already delivered' % order.order_no)

    def cancel(self, request, order):
        # キャンセルフラグを立てるべきだと思うけど...
        pass

    def refund(self, request, order, refund_record):
        pass

    def get_order_info(self, request, order):
        return {
            u'delivered': order.delivered_at is not None
            }


@lbr_view_config(context=ICompleteMailResource, name="delivery-%d" % PLUGIN_ID, renderer=_overridable("shipping_delivery_mail_complete.html", fallback_ua_type='mail'))
@lbr_view_config(context=ILotsElectedMailResource, name="delivery-%d" % PLUGIN_ID, renderer=_overridable("shipping_delivery_mail_complete.html", fallback_ua_type='mail'))
def completion_delivery_mail_viewlet(context, request):
    """ 完了メール表示
    :param context: ICompleteMailResource
    """
    shipping_address = context.order.shipping_address
    return dict(h=cart_helper, shipping_address=shipping_address, 
                notice=context.mail_data("D", "notice")
                )

@lbr_view_config(context=IOrderCancelMailResource, name="delivery-%d" % PLUGIN_ID)
@lbr_view_config(context=ILotsRejectedMailResource, name="delivery-%d" % PLUGIN_ID)
@lbr_view_config(context=ILotsAcceptedMailResource, name="delivery-%d" % PLUGIN_ID)
def notice_mail_viewlet(context, request):
    return Response(text=u"＜配送にてお引取りの方＞\n{0}".format(context.mail_data("D", "notice")))
