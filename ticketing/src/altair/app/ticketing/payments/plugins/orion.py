# -*- coding:utf-8 -*-

from markupsafe import Markup
from collections import namedtuple
import re

from pyramid.response import Response

from altair.app.ticketing.payments.interfaces import IOrderDelivery
from altair.app.ticketing.cart.interfaces import ICartDelivery
from altair.app.ticketing.mails.interfaces import (
    ICompleteMailResource,
    IOrderCancelMailResource,
    ILotsAcceptedMailResource,
    ILotsElectedMailResource,
    ILotsRejectedMailResource,
    )
from altair.pyramid_dynamic_renderer import lbr_view_config
from altair.app.ticketing.cart import helpers as cart_helper

from . import ORION_DELIVERY_PLUGIN_ID as DELIVERY_PLUGIN_ID
from .helpers import get_delivery_method_info

tag_re = re.compile(r"<[^>]*?>")

def includeme(config):
    config.add_delivery_plugin(OrionTicketDeliveryPlugin(), DELIVERY_PLUGIN_ID)
    config.scan(__name__)

def _overridable(path, fallback_ua_type=None):
    from . import _template
    return _template(path, type='overridable', for_='payments', plugin_type='delivery', plugin_id=DELIVERY_PLUGIN_ID, fallback_ua_type=fallback_ua_type)

@lbr_view_config(context=ICartDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer=_overridable("orion_confirm.html"))
def deliver_confirm_viewlet(context, request):
    cart = context.cart
    delivery_method = cart.payment_delivery_pair.delivery_method
    description = get_delivery_method_info(request, delivery_method, 'description')
    return dict(delivery_name=delivery_method.name, description=Markup(description))

QRTicket = namedtuple("QRTicket", "order performance product seat token printed_at")

@lbr_view_config(context=IOrderDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer=_overridable("orion_complete.html"))
def deliver_completion_viewlet(context, request):
    tickets = [ ]
    order = context.order
    delivery_method = order.payment_delivery_pair.delivery_method
    description = get_delivery_method_info(request, delivery_method, 'description')

    for op in order.ordered_products:
        for opi in op.ordered_product_items:
            for t in opi.tokens:
                ticket = QRTicket(
                    order = context.order,
                    performance = context.order.performance,
                    product = opi.product_item,
                    seat = t.seat,
                    token = t,
                    printed_at = t.issued_at)
                tickets.append(ticket)
    
    # TODO: orderreviewから呼ばれた場合とcartの完了画面で呼ばれた場合で
    # 処理を分岐したい

    return dict(
        paid=(order.paid_at!=None),
        order=order,
        tel=order.shipping_address.tel_1,
        tickets=tickets,
        description=Markup(description)
        )

IssuingTime = namedtuple("IssuingTime", "issuing_start_at issuing_end_at")
@lbr_view_config(context=ILotsElectedMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer=_overridable("orion_mail_complete.html", fallback_ua_type='mail'))
@lbr_view_config(context=ICompleteMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer=_overridable("orion_mail_complete.html", fallback_ua_type='mail'))
def deliver_completion_mail_viewlet(context, request):
    order = context.order
    delivery_method = order.payment_delivery_pair.delivery_method
    description = ""
    if delivery_method.description is not None:
        description = tag_re.sub("", delivery_method.description)
    return dict(h=cart_helper,
                notice=context.mail_data("D", "notice"),
                issuing_time = IssuingTime(
                    issuing_start_at=order.issuing_start_at,
                    issuing_end_at=order.issuing_end_at),
                description=description
                )

@lbr_view_config(context=IOrderCancelMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID)
@lbr_view_config(context=ILotsRejectedMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID)
@lbr_view_config(context=ILotsAcceptedMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID)
def delivery_notice_viewlet(context, request):
    return Response(text=u"＜スマートフォンアプリでお受取りの方＞\n{0}".format(context.mail_data("D", "notice")))

class OrionTicketDeliveryPlugin(object):
    def validate_order(self, request, order_like, update=False):
        """ なにかしたほうが良い?"""

    def validate_order_cancellation(self, request, order, now):
        """ キャンセルバリデーション """
        pass

    def prepare(self, request, cart):
        """ 前処理 """

    def finish(self, request, cart):
        """ 確定時処理 """
        pass

    def finish2(self, request, order_like):
        """ 確定時処理 """
        pass

    def finished(self, request, order):
        """ tokenが存在すること """
        pass

    def refresh(self, request, order):
        # XXX: 座席番号などが変わっている可能性があるので、何かすべきような...
        pass

    def cancel(self, request, order, now=None):
        # キャンセルフラグを立てるべきだと思うけど...
        pass

    def refund(self, request, order, refund_record):
        pass

    def get_order_info(self, request, order):
        return {}
