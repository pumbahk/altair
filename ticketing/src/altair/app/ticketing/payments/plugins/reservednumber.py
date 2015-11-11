# -*- coding:utf-8 -*-
import hashlib
import re
import random
import string
from markupsafe import Markup
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from zope.interface import implementer
from sqlalchemy.orm.exc import NoResultFound
from altair.pyramid_dynamic_renderer import lbr_view_config
from altair.app.ticketing.core import models as c_models
from altair.app.ticketing.orders import models as order_models
from altair.app.ticketing.payments.interfaces import IPaymentPlugin, IOrderPayment, IDeliveryPlugin, IOrderDelivery
from altair.app.ticketing.cart.interfaces import ICartDelivery, ICartPayment
from altair.app.ticketing.mails.interfaces import (
    ICompleteMailResource, 
    IOrderCancelMailResource,
    ILotsAcceptedMailResource,
    ILotsElectedMailResource,
    ILotsRejectedMailResource,
    )
from altair.app.ticketing.utils import sensible_alnum_decode

from . import models as m
from . import logger

from . import RESERVE_NUMBER_DELIVERY_PLUGIN_ID as PLUGIN_ID
from . import RESERVE_NUMBER_PAYMENT_PLUGIN_ID as PAYMENT_PLUGIN_ID

tag_re = re.compile(r"<[^>]*?>")

def includeme(config):
    config.add_delivery_plugin(ReservedNumberDeliveryPlugin(), PLUGIN_ID)
    config.add_payment_plugin(ReservedNumberPaymentPlugin(), PAYMENT_PLUGIN_ID)
    config.scan(__name__)

def _overridable_payment(path, fallback_ua_type=None):
    from . import _template
    return _template(path, type='overridable', for_='payments', plugin_type='payment', plugin_id=PAYMENT_PLUGIN_ID, fallback_ua_type=fallback_ua_type)

def _overridable_delivery(path, fallback_ua_type=None):
    from . import _template
    return _template(path, type='overridable', for_='payments', plugin_type='delivery', plugin_id=PLUGIN_ID, fallback_ua_type=fallback_ua_type)

@lbr_view_config(context=IOrderDelivery, name="delivery-%d" % PLUGIN_ID, renderer=_overridable_delivery("reserved_number_completion.html"))
def reserved_number_viewlet(context, request):
    logger.debug(u"窓口")
    order = context.order
    logger.debug(u"order_no = %s" % order.order_no)
    reserved_number = m.ReservedNumber.query.filter_by(order_no=order.order_no).one()
    delivery_method = order.payment_delivery_pair.delivery_method
    return dict(reserved_number=reserved_number, delivery_name=delivery_method.name, description=Markup(delivery_method.description))

@lbr_view_config(context=ICartDelivery, name="delivery-%d" % PLUGIN_ID, renderer=_overridable_delivery("reserved_number_confirm.html"))
def reserved_number_confirm_viewlet(context, request):
    logger.debug(u"窓口")
    cart = context.cart
    delivery_method = cart.payment_delivery_pair.delivery_method
    return dict(delivery_name=delivery_method.name, description=Markup(delivery_method.description))

@lbr_view_config(context=IOrderPayment, name="payment-%d" % PAYMENT_PLUGIN_ID, renderer=_overridable_payment("reserved_number_payment_completion.html"))
def reserved_number_payment_viewlet(context, request):
    logger.debug(u"窓口")
    order = context.order
    logger.debug(u"order_no = %s" % order.order_no)
    reserved_number = m.PaymentReservedNumber.query.filter_by(order_no=order.order_no).first()
    payment_method = order.payment_delivery_pair.payment_method
    return dict(reserved_number=reserved_number, payment_name=payment_method.name, description=Markup(payment_method.description))

@lbr_view_config(context=ICartPayment, name="payment-%d" % PAYMENT_PLUGIN_ID, renderer=_overridable_payment("reserved_number_payment_confirm.html"))
def reserved_number_payment_confirm_viewlet(context, request):
    logger.debug(u"窓口")
    cart = context.cart
    payment_method = cart.payment_delivery_pair.payment_method
    return dict(payment_name=payment_method.name, description=Markup(payment_method.description))


@implementer(IDeliveryPlugin)
class ReservedNumberDeliveryPlugin(object):
    """ 窓口引き換え予約番号プラグイン"""

    def validate_order(self, request, order_like, update=False):
        """ なにかしたほうが良い?""" 

    def prepare(self, request, cart):
        """ 前処理 なし"""

    def finish(self, request, cart):
        """ 確定処理 """
        self.finish2(request, cart)

    def finish2(self, request, order_like):
        while True:
            number = rand_string(string.digits, 10)
            existing_number = m.ReservedNumber.query.filter_by(number=number).first()
            if existing_number is None:
                reserved_number = m.ReservedNumber(order_no=order_like.order_no, number=number)
                break
        m.DBSession.add(reserved_number)
        logger.debug(u"窓口引き換え番号: %s" % reserved_number.number)

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

    def get_order_info(self, request, order):
        try:
            reserved_number = m.DBSession.query(m.ReservedNumber).filter(
                m.ReservedNumber.order_no==order.order_no).one().number
        except NoResultFound:
            reserved_number = u''
        return {
            u'reserved_number': reserved_number,
            }

@view_defaults(context=ICompleteMailResource)
class CompletionMailViewlet(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(name="payment-%d" % PAYMENT_PLUGIN_ID, renderer=_overridable_payment("reserved_number_payment_mail_complete.html", fallback_ua_type='mail'))
    def payment(self):
        """ 完了メール表示
        :param context: ICompleteMailDelivery
        """
        notice = self.context.mail_data("P", "notice")
        return dict(notice=notice)

    @lbr_view_config(name="delivery-%d" % PLUGIN_ID, renderer=_overridable_delivery("reserved_number_mail_complete.html", fallback_ua_type='mail'))
    def delivery(self):
        """ 完了メール表示
        :param context: ICompleteMailDelivery
        """
        order = self.context.order
        delivery_method = order.payment_delivery_pair.delivery_method
        notice = self.context.mail_data("D", "notice")
        reserved_number = m.ReservedNumber.query.filter_by(order_no=self.context.order.order_no).first()
        return dict(notice=notice, reserved_number=reserved_number, description=tag_re.sub("", delivery_method.description))

@view_defaults(context=IOrderCancelMailResource)
class OrderCancelMailViewlet(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(name="payment-%d" % PAYMENT_PLUGIN_ID)
    def payment(self):
        """ cancelメール表示
        """
        return Response(self.context.mail_data("P", "notice"))

    @lbr_view_config(name="delivery-%d" % PLUGIN_ID)
    def delivery(self):
        """ cancelメール表示
        """
        return Response(self.context.mail_data("D", "notice"))

@lbr_view_config(context=ILotsElectedMailResource, name="payment-%d" % PAYMENT_PLUGIN_ID)
@lbr_view_config(context=ILotsRejectedMailResource, name="payment-%d" % PAYMENT_PLUGIN_ID)
@lbr_view_config(context=ILotsAcceptedMailResource, name="payment-%d" % PAYMENT_PLUGIN_ID)
def lot_payment_notice_viewlet(context, request):
    return Response(context.mail_data("P", "notice"))

@lbr_view_config(context=ILotsElectedMailResource, name="delivery-%d" % PLUGIN_ID)
@lbr_view_config(context=ILotsRejectedMailResource, name="delivery-%d" % PLUGIN_ID)
@lbr_view_config(context=ILotsAcceptedMailResource, name="delivery-%d" % PLUGIN_ID)
def lot_delivery_notice_viewlet(context, request):
    return Response(context.mail_data("D", "notice"))

def rand_string(seed, length):
    return "".join([random.choice(seed) for i in range(length)])

@implementer(IPaymentPlugin)
class ReservedNumberPaymentPlugin(object):
    """ 窓口支払い番号プラグイン"""

    def validate_order(self, request, order_like, update=False):
        """ なにかしたほうが良い?""" 

    def prepare(self, request, cart):
        """ 前処理 なし"""

    def finish(self, request, cart):
        order = order_models.Order.create_from_cart(cart)
        self.finish2(request, order)
        cart.finish()
        return order

    def finish2(self, request, order_like):
        """ 確定処理 """
        while True:
            number = rand_string(string.digits, 10)
            existing_number = m.PaymentReservedNumber.query.filter_by(number=number).first()
            if existing_number is None:
                reserved_number = m.PaymentReservedNumber(order_no=order_like.order_no, number=number)
                break
        m.DBSession.add(reserved_number)
        logger.debug(u"支払番号: %s" % reserved_number.number)

    def finished(self, request, order):
        """ 支払番号が発行されていること """
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

    def get_order_info(self, request, order):
        try:
            reserved_number = m.DBSession.query(m.PaymentReservedNumber).filter(
                m.PaymentReservedNumber.order_no==order.order_no).one().number
        except NoResultFound:
            reserved_number = u'' 
        return {
            u'reserved_number': reserved_number,
            }

