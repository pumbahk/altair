# -*- coding:utf-8 -*-
import hashlib
import random
import string
from pyramid.view import view_config
from pyramid.response import Response
from zope.interface import implementer
from ticketing.core import models as c_models
from ..interfaces import IDeliveryPlugin, IOrderDelivery, ICartDelivery, ICompleteMailDelivery, ICompleteMailPayment, IOrderCancelMailDelivery, IOrderCancelMailPayment
from ..interfaces import IPaymentPlugin, IOrderPayment, ICartPayment
from . import models as m
from . import logger

PLUGIN_ID = 3
PAYMENT_PLUGIN_ID = 4

def includeme(config):
    config.add_delivery_plugin(ReservedNumberDeliveryPlugin(), PLUGIN_ID)
    config.add_payment_plugin(ReservedNumberPaymentPlugin(), PAYMENT_PLUGIN_ID)
    config.scan(__name__)

@view_config(context=IOrderDelivery, name="delivery-%d" % PLUGIN_ID, renderer="ticketing.cart.plugins:templates/reserved_number_completion.html")
def reserved_number_viewlet(context, request):
    logger.debug(u"窓口")
    order = context.order
    logger.debug(u"order_no = %s" % order.order_no)
    reserved_number = m.ReservedNumber.query.filter_by(order_no=order.order_no).one()
    return dict(reserved_number=reserved_number)

@view_config(context=ICartDelivery, name="delivery-%d" % PLUGIN_ID, renderer="ticketing.cart.plugins:templates/reserved_number_confirm.html")
def reserved_number_confirm_viewlet(context, request):
    logger.debug(u"窓口")
    return dict()

@view_config(context=IOrderPayment, name="payment-%d" % PAYMENT_PLUGIN_ID, renderer="ticketing.cart.plugins:templates/reserved_number_payment_completion.html")
def reserved_number_payment_viewlet(context, request):
    logger.debug(u"窓口")
    order = context.order
    logger.debug(u"order_no = %s" % order.order_no)
    reserved_number = m.PaymentReservedNumber.query.filter_by(order_no=order.order_no).one()
    return dict(reserved_number=reserved_number)

@view_config(context=ICartPayment, name="payment-%d" % PAYMENT_PLUGIN_ID, renderer="ticketing.cart.plugins:templates/reserved_number_payment_confirm.html")
def reserved_number_payment_confirm_viewlet(context, request):
    logger.debug(u"窓口")
    return dict()


@implementer(IDeliveryPlugin)
class ReservedNumberDeliveryPlugin(object):
    """ 窓口引き換え予約番号プラグイン"""
    def prepare(self, request, cart):
        """ 前処理 なし"""

    def finish(self, request, cart):
        """ 確定処理 """
        number = hashlib.md5(str(cart.id)).hexdigest()
        reserved_number = m.ReservedNumber(order_no=cart.order_no, number=number)
        m.DBSession.add(reserved_number)
        logger.debug("引き換え番号: %s" % reserved_number.number)

@view_config(context=ICompleteMailPayment, name="payment-%d" % PAYMENT_PLUGIN_ID)
@view_config(context=ICompleteMailDelivery, name="delivery-%d" % PLUGIN_ID, renderer="ticketing.cart.plugins:templates/reserved_number_mail_complete.html")
def completion_delivery_mail_viewlet(context, request):
    """ 完了メール表示
    :param context: ICompleteMailDelivery
    """
    notice=context.mail_data("notice")
    return dict(notice=notice)

@view_config(context=IOrderCancelMailPayment, name="payment-%d" % PAYMENT_PLUGIN_ID)
@view_config(context=IOrderCancelMailDelivery, name="delivery-%d" % PLUGIN_ID)
def cancel_payment_mail_viewlet(context, request):
    """ cancelメール表示
    """
    return Response(context.mail_data("notice"))

def rand_string(seed, length):
    return "".join([random.choice(seed) for i in range(length)])

@implementer(IPaymentPlugin)
class ReservedNumberPaymentPlugin(object):
    """ 窓口支払い番号プラグイン"""
    def prepare(self, request, cart):
        """ 前処理 なし"""

    def finish(self, request, cart):
        """ 確定処理 """
        while True:
            number = rand_string(string.digits, 10)
            existing_number = m.PaymentReservedNumber.query.filter_by(number=number).first()
            if existing_number is None:
                reserved_number = m.PaymentReservedNumber(order_no=cart.order_no, number=number)
                break
        m.DBSession.add(reserved_number)
        logger.debug("支払い番号: %s" % reserved_number.number)
        order = c_models.Order.create_from_cart(cart)
        cart.finish()

        return order
