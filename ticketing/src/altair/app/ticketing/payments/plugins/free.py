# -*- coding:utf-8 -*-
import hashlib
import random
import string
from markupsafe import Markup
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from zope.interface import implementer
from altair.pyramid_dynamic_renderer import lbr_view_config
from altair.app.ticketing.core import models as c_models
from altair.app.ticketing.orders import models as order_models
from altair.app.ticketing.payments.interfaces import IPaymentPlugin, IOrderPayment
from altair.app.ticketing.cart.interfaces import ICartPayment
from altair.app.ticketing.mails.interfaces import (
    ICompleteMailResource, 
    IOrderCancelMailResource,
    ILotsAcceptedMailResource,
    ILotsElectedMailResource,
    ILotsRejectedMailResource,
    )
from ..exceptions import OrderLikeValidationFailure

from . import logger

from . import FREE_PAYMENT_PLUGIN_ID as PAYMENT_PLUGIN_ID

def includeme(config):
    config.add_payment_plugin(FreePaymentPlugin(), PAYMENT_PLUGIN_ID)
    config.scan(__name__)

def _overridable_payment(path, fallback_ua_type=None):
    from . import _template
    return _template(path, type='overridable', for_='payments', plugin_type='payment', plugin_id=PAYMENT_PLUGIN_ID, fallback_ua_type=fallback_ua_type)

@lbr_view_config(context=IOrderPayment, name="payment-%d" % PAYMENT_PLUGIN_ID, renderer=_overridable_payment("free_payment_completion.html"))
def reserved_number_payment_viewlet(context, request):
    order = context.order
    payment_method = order.payment_delivery_pair.payment_method
    return dict(payment_name=payment_method.name, description=Markup(payment_method.description))

@lbr_view_config(context=ICartPayment, name="payment-%d" % PAYMENT_PLUGIN_ID, renderer=_overridable_payment("free_payment_confirm.html"))
def reserved_number_payment_confirm_viewlet(context, request):
    cart = context.cart
    payment_method = cart.payment_delivery_pair.payment_method
    return dict(payment_name=payment_method.name, description=Markup(payment_method.description))

@lbr_view_config(context=ICompleteMailResource, name="payment-%d" % PAYMENT_PLUGIN_ID, renderer=_overridable_payment("free_mail_complete.html", fallback_ua_type='mail'))
def complete_mail(context, request):
    notice = context.mail_data("P", "notice")
    return dict(notice=notice)

@lbr_view_config(context=IOrderCancelMailResource, name="payment-%d" % PAYMENT_PLUGIN_ID)
def cancel_mail(context, request):
    return Response(context.mail_data("P", "notice"))

@lbr_view_config(context=ILotsElectedMailResource, name="payment-%d" % PAYMENT_PLUGIN_ID)
@lbr_view_config(context=ILotsRejectedMailResource, name="payment-%d" % PAYMENT_PLUGIN_ID)
@lbr_view_config(context=ILotsAcceptedMailResource, name="payment-%d" % PAYMENT_PLUGIN_ID)
def lot_payment_notice_viewlet(context, request):
    return Response(context.mail_data("P", "notice"))

@implementer(IPaymentPlugin)
class FreePaymentPlugin(object):
    """ 窓口支払い番号プラグイン"""

    def validate_order(self, request, order_like, update=False):
        if order_like.total_amount != 0:
            raise OrderLikeValidationFailure(u'total_amount is not zero', 'order.total_amount')

    def validate_order_cancellation(self, request, order, now):
        """ キャンセルバリデーション """
        pass

    def prepare(self, request, cart):
        """ 前処理 なし"""

    def finish(self, request, cart):
        """ 確定処理 """
        order = order_models.Order.create_from_cart(cart)
        from datetime import datetime
        order.paid_at = datetime.now()
        cart.finish()
        return order

    def finish2(self, request, order_like):
        # 何もしなくてよい
        return

    def finished(self, request, order):
        return True

    def refresh(self, request, order):
        pass

    def cancel(self, request, order, now=None):
        pass

    def refund(self, request, order, refund_record):
        pass

    def get_order_info(self, request, order):
        return {}

