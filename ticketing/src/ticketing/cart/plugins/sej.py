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

from ticketing.sej.payment import request_order
from ticketing.sej.resources import SejPaymentType

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

        user_profile  = order.user.user_profile

        sej_order = request_order(
            shop_name           = order.ordered_from.name,
            shop_id             = u'30520',
            contact_01          = u'',
            contact_02          = u'',
            order_id            = order.order_no,
            username            = '%s %s' % (user_profile.last_name, user_profile.first_name),
            username_kana       = '%s %s' % (user_profile.last_name_kana, user_profile.first_name_kana),
            tel                 = user_profile.tel,
            zip                 = user_profile.zip,
            email               = user_profile.email,
            total               = 0,
            ticket_total        = 0,
            commission_fee      = 0,
            payment_type        = SejPaymentType.PrepaymentOnly,
            ticketing_fee       = 0,
            payment_due_at      = None,
            ticketing_start_at  = None,
            ticketing_due_at    = None,
            regrant_number_due_at = None
        )

        request.session['sej_order'] = sej_order
        request.session['order'] = order

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
    sej_order = request.session['sej_order']
    order = request.session['order']
    return dict(
        order=order,
        sej_order=sej_order
    )


@view_config(context=ICartDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID)
def sej_delivery_confirm_viewlet(context, request):
    return Response(text=u'コンビニ受け取り')

@view_config(context=IOrderPayment, name="payment-%d" % PAYMENT_PLUGIN_ID, renderer="ticketing.cart.plugins:templates/sej_exchange_sheet.html")
def sej_payment_viewlet(context, request):
    sej_order = request.session['sej_order']
    order = request.session['order']
    return dict(
        order=order,
        sej_order=sej_order
    )

@view_config(context=ICartPayment, name="payment-%d" % PAYMENT_PLUGIN_ID)
def sej_payment_confirm_viewlet(context, request):
    sej_order = request.session['sej_order']
    order = request.session['order']
    return dict(
        order=order,
        sej_order=sej_order
    )

