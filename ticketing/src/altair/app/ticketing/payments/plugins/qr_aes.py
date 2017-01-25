# -*- coding:utf-8 -*-

from markupsafe import Markup
from altair.pyramid_dynamic_renderer import lbr_view_config
from altair.app.ticketing.payments.interfaces import IOrderDelivery
from altair.app.ticketing.cart.interfaces import ICartDelivery
from altair.app.ticketing.mails.interfaces import (
    ICompleteMailResource,
    IOrderCancelMailResource,
    ILotsAcceptedMailResource,
    ILotsElectedMailResource,
    ILotsRejectedMailResource,
    )
from . import logger
from pyramid.response import Response
from altair.app.ticketing.cart import helpers as cart_helper
from altair.app.ticketing.core.interfaces import IOrderLike
from collections import namedtuple

from . import QR_AES_DELIVERY_PLUGIN_ID as DELIVERY_PLUGIN_ID
import re
tag_re = re.compile(r"<[^>]*?>")


def includeme(config):
    config.add_delivery_plugin(QRAESTicketDeliveryPlugin(), DELIVERY_PLUGIN_ID)
    config.scan(__name__)

def _overridable(path, fallback_ua_type=None):
    from . import _template
    return _template(path, type='overridable', for_='payments', plugin_type='delivery', plugin_id=DELIVERY_PLUGIN_ID, fallback_ua_type=fallback_ua_type)

@lbr_view_config(context=ICartDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer=_overridable("qr_aes_confirm.html"))
def deliver_confirm_viewlet(context, request):
    cart = context.cart
    delivery_method = cart.payment_delivery_pair.delivery_method
    return dict(delivery_name=delivery_method.name, description=Markup(delivery_method.description))

QRTicket = namedtuple("QRTicket", "order performance product seat token printed_at")

@lbr_view_config(context=IOrderDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer=_overridable("qr_aes_complete.html"))
def deliver_completion_viewlet(context, request):
    order = context.order
    logger.debug(u"order_no = %s" % order.order_no)
    delivery_method = order.payment_delivery_pair.delivery_method

    tickets = [ ]

    for op in order.ordered_products:
        for opi in op.ordered_product_items:
            for t in opi.tokens:
                ticket = QRTicket(
                    order = context.order,
                    performance=context.order.performance,
                    product=op.product,
                    seat = t.seat,
                    token = t,
                    printed_at=t.issued_at
                )
                tickets.append(ticket)

    # TODO: orderreviewから呼ばれた場合とcartの完了画面で呼ばれた場合で
    # 処理を分岐したい
    from altair.app.ticketing.payments.plugins import FREE_PAYMENT_PLUGIN_ID
    return dict(
        paid = (order.paid_at != None),
        free = (order.payment_delivery_pair.payment_method.payment_plugin_id == FREE_PAYMENT_PLUGIN_ID),
        order = order,
        tel = order.shipping_address.tel_1,
        tickets = tickets,
        delivery_name=delivery_method.name,
        description=Markup(delivery_method.description),
        )

@lbr_view_config(context=ICompleteMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer=_overridable("qr_aes_mail_complete.html", fallback_ua_type='mail'))
def deliver_completion_mail_viewlet(context, request):
    shipping_address = context.order.shipping_address
    order = context.order
    delivery_method = order.payment_delivery_pair.delivery_method
    description = ""
    if delivery_method.description is not None:
        description = tag_re.sub("", delivery_method.description)
    return dict(h=cart_helper, shipping_address=shipping_address,
                notice=context.mail_data("D", "notice"),
                delivery_name=delivery_method.name,
                description=description,
                )

@lbr_view_config(context=IOrderCancelMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID)
@lbr_view_config(context=ILotsRejectedMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID)
@lbr_view_config(context=ILotsAcceptedMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID)
@lbr_view_config(context=ILotsElectedMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID)
def delivery_notice_viewlet(context, request):
    return Response(text=u"＜QRでのお受取りの方＞\n{0}".format(context.mail_data("D", "notice")))

class QRAESTicketDeliveryPlugin(object):
    def validate_order(self, request, order_like, update=False):
        """ なにかしたほうが良い?"""
        pass

    def validate_order_cancellation(self, request, order, now):
        """ キャンセルバリデーション """
        pass

    def prepare(self, request, cart):
        """ 前処理 """
        pass

    def finish(self, request, cart):
        """ 確定時処理 """
        pass

    def finish2(self, request, order_like):
        """ 確定時処理 """
        pass

    def finished(self, request, order):
        """ tokenが存在すること """
        result = True
        if isinstance(order, IOrderLike):
            for op in order.items:
                for opi in op.elements:
                    result = result and opi.tokens
        return result

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
