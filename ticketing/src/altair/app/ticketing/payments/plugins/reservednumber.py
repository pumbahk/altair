# -*- coding:utf-8 -*-
import hashlib
import random
import string
from markupsafe import Markup
from pyramid.view import view_config
from pyramid.response import Response
from zope.interface import implementer
from altair.app.ticketing.core import models as c_models
from altair.app.ticketing.orders import models as order_models
from altair.app.ticketing.payments.interfaces import IPaymentPlugin, IOrderPayment, IDeliveryPlugin, IOrderDelivery
from altair.app.ticketing.cart.interfaces import ICartDelivery, ICartPayment
from altair.app.ticketing.mails.interfaces import (
    ICompleteMailDelivery, 
    ICompleteMailPayment, 
    IOrderCancelMailDelivery, 
    IOrderCancelMailPayment,
    ILotsAcceptedMailPayment,
    ILotsAcceptedMailDelivery,
    ILotsElectedMailPayment,
    ILotsElectedMailDelivery,
    ILotsRejectedMailPayment,
    ILotsRejectedMailDelivery,
)
from altair.app.ticketing.utils import sensible_alnum_decode

from . import models as m
from . import logger

from . import RESERVE_NUMBER_DELIVERY_PLUGIN_ID as PLUGIN_ID
from . import RESERVE_NUMBER_PAYMENT_PLUGIN_ID as PAYMENT_PLUGIN_ID

def includeme(config):
    config.add_delivery_plugin(ReservedNumberDeliveryPlugin(), PLUGIN_ID)
    config.add_payment_plugin(ReservedNumberPaymentPlugin(), PAYMENT_PLUGIN_ID)
    config.scan(__name__)

def _overridable_payment(path):
    from . import _template
    if _template is None:
        return '%s:templates/%s' % (__name__, path)
    else:
        return _template(path, type='overridable', for_='payments', plugin_type='payment', plugin_id=PAYMENT_PLUGIN_ID)

def _overridable_delivery(path):
    from . import _template
    if _template is None:
        return '%s:templates/%s' % (__name__, path)
    else:
        return _template(path, type='overridable', for_='payments', plugin_type='delivery', plugin_id=PLUGIN_ID)

@view_config(context=IOrderDelivery, name="delivery-%d" % PLUGIN_ID, renderer=_overridable_delivery("reserved_number_completion.html"))
def reserved_number_viewlet(context, request):
    logger.debug(u"窓口")
    order = context.order
    logger.debug(u"order_no = %s" % order.order_no)
    reserved_number = m.ReservedNumber.query.filter_by(order_no=order.order_no).one()
    delivery_method = order.payment_delivery_pair.delivery_method
    return dict(reserved_number=reserved_number, delivery_name=delivery_method.name, description=Markup(delivery_method.description))

@view_config(context=ICartDelivery, name="delivery-%d" % PLUGIN_ID, renderer=_overridable_delivery("reserved_number_confirm.html"))
def reserved_number_confirm_viewlet(context, request):
    logger.debug(u"窓口")
    cart = context.cart
    delivery_method = cart.payment_delivery_pair.delivery_method
    return dict(delivery_name=delivery_method.name, description=Markup(delivery_method.description))

@view_config(context=IOrderPayment, name="payment-%d" % PAYMENT_PLUGIN_ID, renderer=_overridable_payment("reserved_number_payment_completion.html"))
def reserved_number_payment_viewlet(context, request):
    logger.debug(u"窓口")
    order = context.order
    logger.debug(u"order_no = %s" % order.order_no)
    reserved_number = m.PaymentReservedNumber.query.filter_by(order_no=order.order_no).first()
    payment_method = order.payment_delivery_pair.payment_method
    return dict(reserved_number=reserved_number, payment_name=payment_method.name, description=Markup(payment_method.description))

@view_config(context=ICartPayment, name="payment-%d" % PAYMENT_PLUGIN_ID, renderer=_overridable_payment("reserved_number_payment_confirm.html"))
def reserved_number_payment_confirm_viewlet(context, request):
    logger.debug(u"窓口")
    cart = context.cart
    payment_method = cart.payment_delivery_pair.payment_method
    return dict(payment_name=payment_method.name, description=Markup(payment_method.description))


@implementer(IDeliveryPlugin)
class ReservedNumberDeliveryPlugin(object):
    """ 窓口引き換え予約番号プラグイン"""

    def validate_order(self, request, order_like):
        """ なにかしたほうが良い?""" 

    def prepare(self, request, cart):
        """ 前処理 なし"""

    def finish(self, request, cart):
        """ 確定処理 """
        self.finish2(request, cart)

    def finish2(self, request, order_like):
        seq_no = sensible_alnum_decode(order_like.order_no[2:])
        logger.debug('seq_no = %s' % seq_no)
        number = hashlib.md5(str(seq_no)).hexdigest()
        reserved_number = m.ReservedNumber(order_no=order_like.order_no, number=number)
        m.DBSession.add(reserved_number)

    def finished(self, request, order):
        """ 引換番号が発行されていること """
        reserved_number = m.DBSession.query(m.ReservedNumber).filter(
            m.ReservedNumber.order_no==order.order_no).first()
        return bool(reserved_number)

    def refresh(self, request, order):
        if order.delivered_at is not None:
            raise Exception('order %s is already delivered' % order.order_no)
        # 引換番号を再発行するべきだと思うけど...

    def cancel(self, request, order):
        # キャンセルフラグを立てるべきだと思うけど...
        pass

    def refund(self, request, order, refund_record):
        pass

@view_config(context=ICompleteMailPayment, name="payment-%d" % PAYMENT_PLUGIN_ID, renderer=_overridable_payment("reserved_number_payment_mail_complete.html"))
@view_config(context=ICompleteMailDelivery, name="delivery-%d" % PLUGIN_ID, renderer=_overridable_delivery("reserved_number_mail_complete.html"))
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

@view_config(context=ILotsElectedMailPayment, name="payment-%d" % PAYMENT_PLUGIN_ID)
@view_config(context=ILotsRejectedMailPayment, name="payment-%d" % PAYMENT_PLUGIN_ID)
@view_config(context=ILotsAcceptedMailPayment, name="payment-%d" % PAYMENT_PLUGIN_ID)
@view_config(context=ILotsElectedMailDelivery, name="delivery-%d" % PLUGIN_ID)
@view_config(context=ILotsRejectedMailDelivery, name="delivery-%d" % PLUGIN_ID)
@view_config(context=ILotsAcceptedMailDelivery, name="delivery-%d" % PLUGIN_ID)
def notice_viewlet(context, request):
    return Response(context.mail_data("notice"))

def rand_string(seed, length):
    return "".join([random.choice(seed) for i in range(length)])

@implementer(IPaymentPlugin)
class ReservedNumberPaymentPlugin(object):
    """ 窓口支払い番号プラグイン"""

    def validate_order(self, request, order_like):
        """ なにかしたほうが良い?""" 

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
        logger.debug(u"支払い番号: %s" % reserved_number.number)
        order = order_models.Order.create_from_cart(cart)
        cart.finish()

        return order

    def finished(self, request, order):
        """ 支払い番号が発行されていること """
        reserved_number = m.DBSession.query(m.PaymentReservedNumber).filter(
            m.PaymentReservedNumber.order_no==order.order_no).first()
        return bool(reserved_number)

    def refresh(self, request, order):
        if order.delivered_at is not None:
            raise Exception('order %s is already delivered' % order.order_no)
        # 支払番号を再発行すべきだと思うけど...

    def cancel(self, request, order):
        # キャンセルフラグを立てるべきだと思うけど...
        pass

    def refund(self, request, order, refund_record):
        pass
