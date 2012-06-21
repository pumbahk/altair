# -*- coding:utf-8 -*-

from pyramid.view import view_config
from pyramid.response import Response
from zope.interface import implementer
from .interfaces import IDeliveryPlugin, IOrderDelivery, ICartDelivery
from . import models as m
from . import logger

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
    return dict(shipping_address=cart.shipping_address)

class ShippingDeliveryPlugin(object):
    def prepare(self, request, cart):
        """ 前処理なし """

    def finish(self, request, cart):
        """ 確定処理なし """
