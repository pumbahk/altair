# -*- coding:utf-8 -*-

from pyramid.view import view_config
from pyramid.response import Response
from zope.interface import implementer
from altair.app.ticketing.payments.interfaces import IDeliveryPlugin, IOrderDelivery
from altair.app.ticketing.cart.interfaces import ICartDelivery
from altair.app.ticketing.mails.interfaces import ICompleteMailDelivery, IOrderCancelMailDelivery
from altair.app.ticketing.mails.interfaces import ILotsAcceptedMailDelivery
from altair.app.ticketing.mails.interfaces import ILotsElectedMailDelivery
from altair.app.ticketing.mails.interfaces import ILotsRejectedMailDelivery

from . import models as m
from . import logger
from altair.app.ticketing.cart import helpers as cart_helper
from altair.app.ticketing.core import models as c_models

from . import SHIPPING_DELIVERY_PLUGIN_ID as PLUGIN_ID

def includeme(config):
    config.add_delivery_plugin(ShippingDeliveryPlugin(), PLUGIN_ID)
    config.scan(__name__)

@view_config(context=ICartDelivery, name="delivery-1", renderer="altair.app.ticketing.payments.plugins:templates/shipping_confirm.html")
def deliver_confirm_viewlet(context, request):
    logger.debug(u"郵送")
    cart = context.cart
    return dict(shipping_address=cart.shipping_address)

@view_config(context=IOrderDelivery, name="delivery-1", renderer="altair.app.ticketing.payments.plugins:templates/shipping_confirm.html")
def deliver_completion_viewlet(context, request):
    logger.debug(u"郵送")
    order = context.order
    return dict(shipping_address=order.shipping_address, order=order)

class ShippingDeliveryPlugin(object):
    def prepare(self, request, cart):
        """ 前処理なし """

    def finish(self, request, cart):
        """ 確定処理なし """

    def finished(self, request, order):
        """ shipping addressがあればOK?"""
        return bool(order.shipping_address)

    def refresh(self, request, order):
        if order.delivered_at is not None:
            raise Exception('order %s is already delivered' % order.order_no)

@view_config(context=ICompleteMailDelivery, name="delivery-%d" % PLUGIN_ID, renderer="altair.app.ticketing.payments.plugins:templates/shipping_delivery_mail_complete.html")
@view_config(context=ILotsElectedMailDelivery, name="delivery-%d" % PLUGIN_ID, renderer="altair.app.ticketing.payments.plugins:templates/shipping_delivery_mail_complete.html")
def completion_delivery_mail_viewlet(context, request):
    """ 完了メール表示
    :param context: ICompleteMailDelivery
    """
    shipping_address = context.order.shipping_address
    return dict(h=cart_helper, shipping_address=shipping_address, 
                notice=context.mail_data("notice")
                )

@view_config(context=IOrderCancelMailDelivery, name="delivery-%d" % PLUGIN_ID)
@view_config(context=ILotsRejectedMailDelivery, name="delivery-%d" % PLUGIN_ID)
@view_config(context=ILotsAcceptedMailDelivery, name="delivery-%d" % PLUGIN_ID)
def notice_mail_viewlet(context, request):
    return Response(text=u"＜配送にてお引取りの方＞\n{0}".format(context.mail_data("notice")))
