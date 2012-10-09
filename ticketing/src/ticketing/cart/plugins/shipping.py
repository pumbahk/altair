# -*- coding:utf-8 -*-

from pyramid.view import view_config
from pyramid.response import Response
from zope.interface import implementer
from ..interfaces import IDeliveryPlugin, IOrderDelivery, ICartDelivery, ICompleteMailDelivery, IOrderCancelMailDelivery
from . import models as m
from . import logger
from ticketing.cart import helpers as cart_helper
from ticketing.core import models as c_models

PLUGIN_ID = 1
def includeme(config):
    config.add_delivery_plugin(ShippingDeliveryPlugin(), PLUGIN_ID)
    config.scan(__name__)

@view_config(context=ICartDelivery, name="delivery-1", renderer="ticketing.cart.plugins:templates/shipping_confirm.html")
def deliver_confirm_viewlet(context, request):
    logger.debug(u"郵送")
    cart = context.cart
    return dict(shipping_address=cart.shipping_address)

@view_config(context=IOrderDelivery, name="delivery-1", renderer="ticketing.cart.plugins:templates/shipping_confirm.html")
def deliver_completion_viewlet(context, request):
    logger.debug(u"郵送")
    order = context.order
    return dict(shipping_address=order.shipping_address, order=order)

class ShippingDeliveryPlugin(object):
    def prepare(self, request, cart):
        """ 前処理なし """

    def finish(self, request, cart):
        """ 確定処理なし """

@view_config(context=ICompleteMailDelivery, name="delivery-%d" % PLUGIN_ID, renderer="ticketing.cart.plugins:templates/shipping_delivery_mail_complete.html")
def completion_delivery_mail_viewlet(context, request):
    """ 完了メール表示
    :param context: ICompleteMailDelivery
    """
    shipping_address = context.order.shipping_address
    return dict(h=cart_helper, shipping_address=shipping_address, 
                notice=context.mail_data("notice")
                )

@view_config(context=IOrderCancelMailDelivery, name="delivery-%d" % PLUGIN_ID)
def cancel_delivery_mail_viewlet(context, request):
    """ cancelメール表示
    :param context: IOrderCancelMailDelivery
    """
    return Response(context.mail_data("notice"))
