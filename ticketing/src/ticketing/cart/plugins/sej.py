# -*- coding:utf-8 -*-
from zope.interface import implementer
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound

from .interfaces import IPaymentPlugin, ICartPayment, IOrderPayment
from .interfaces import IDeliveryPlugin, ICartDelivery, IOrderDelivery
from .interfaces import IPaymentDeliveryPlugin
from .models import DBSession
from ticketing.orders import models as o_models
from .. import schema
from .. import logger
from .. import helpers as h

PAYMENT_PLUGIN_ID = 3
DELIVERY_PLUGIN_ID = 2

def includeme(config):
    # 決済系(マルチ決済)
    config.add_payment_plugin(SejPaymentPlugin(), PAYMENT_PLUGIN_ID)
    config.add_delivery_plugin(SejDeliveryPlugin(), DELIVERY_PLUGIN_ID)
    config.add_payment_delivery_plugin(SejPaymentDeliveryPlugin(), PAYMENT_PLUGIN_ID, DELIVERY_PLUGIN_ID)
    config.scan(__name__)

@implementer(IPaymentPlugin)
class SejPaymentPlugin(object):

    def prepare(self, request, cart):
        """  """

    def finish(self, request, cart):
        """ 売り上げ確定 """
        logger.debug('Sej Payment')
        order = o_models.Order.create_from_cart(cart)
        cart.finish()

        return order

@implementer(IDeliveryPlugin)
class SejDeliveryPlugin(object):
    def prepare(self, request, cart):
        """  """

    def finish(self, request, cart):
        logger.debug('Sej Delivery')
        """  """

@implementer(IDeliveryPlugin)
class SejPaymentDeliveryPlugin(object):
    def prepare(self, request, cart):
        """  """

    def finish(self, request, cart):
        """  """
        logger.debug('Sej Payment and Delivery')
        order = o_models.Order.create_from_cart(cart)
        cart.finish()

        return order

@view_config(context=IOrderDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID)
def sej_delivery_viewlet(context, request):
    return Response(text=u'コンビニ受け取り 発券番号')

@view_config(context=ICartDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID)
def sej_delivery_confirm_viewlet(context, request):
    return Response(text=u'コンビニ受け取り')

@view_config(context=IOrderPayment, name="payment-%d" % PAYMENT_PLUGIN_ID)
def sej_payment_viewlet(context, request):
    return Response(text=u'コンビニ決済 支払い番号')

@view_config(context=ICartPayment, name="payment-%d" % PAYMENT_PLUGIN_ID)
def sej_payment_confirm_viewlet(context, request):
    return Response(text=u'コンビニ決済')
