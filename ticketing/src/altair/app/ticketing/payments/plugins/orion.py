# -*- coding:utf-8 -*-

from altair.app.ticketing.payments.interfaces import IOrderDelivery
from altair.app.ticketing.cart.interfaces import ICartDelivery
from altair.app.ticketing.mails.interfaces import (
    ICompleteMailResource,
    IOrderCancelMailResource,
    ILotsAcceptedMailResource,
    ILotsElectedMailResource,
    ILotsRejectedMailResource,
    )

from . import models as m
from altair.app.ticketing.core import models as core_models
from . import logger
import qrcode
import StringIO
from pyramid.response import Response
from altair.pyramid_dynamic_renderer import lbr_view_config
from altair.app.ticketing.qr import qr
from altair.app.ticketing.cart import helpers as cart_helper
from altair.app.ticketing.core import models as c_models
from collections import namedtuple

from . import ORION_DELIVERY_PLUGIN_ID as DELIVERY_PLUGIN_ID

def includeme(config):
    config.add_delivery_plugin(OrionTicketDeliveryPlugin(), DELIVERY_PLUGIN_ID)
    config.scan(__name__)

def _overridable(path, fallback_ua_type=None):
    from . import _template
    return _template(path, type='overridable', for_='payments', plugin_type='delivery', plugin_id=DELIVERY_PLUGIN_ID, fallback_ua_type=fallback_ua_type)

@lbr_view_config(context=ICartDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer=_overridable("orion_confirm.html"))
def deliver_confirm_viewlet(context, request):
    return dict()

QRTicket = namedtuple("QRTicket", "order performance product seat token printed_at")

@lbr_view_config(context=IOrderDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer=_overridable("orion_complete.html"))
def deliver_completion_viewlet(context, request):
    tickets = [ ]
    order = context.order
    for op in order.ordered_products:
        for opi in op.ordered_product_items:
            for t in opi.tokens:
                ticket = QRTicket(
                    order = context.order,
                    performance = context.order.performance,
                    product = op.product,
                    seat = t.seat,
                    token = t,
                    printed_at = t.issued_at)
                tickets.append(ticket)
    
    # TODO: orderreviewから呼ばれた場合とcartの完了画面で呼ばれた場合で
    # 処理を分岐したい
    
    return dict(
        paid = (order.paid_at != None),
        order = order,
        tel = order.shipping_address.tel_1,
        tickets = tickets,
        )

@lbr_view_config(context=ICompleteMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer=_overridable("orion_mail_complete.html", fallback_ua_type='mail'))
def deliver_completion_mail_viewlet(context, request):
    shipping_address = context.order.shipping_address
    return dict(h=cart_helper, shipping_address=shipping_address, 
                notice=context.mail_data("D", "notice")
                )

@lbr_view_config(context=IOrderCancelMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID)
@lbr_view_config(context=ILotsRejectedMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID)
@lbr_view_config(context=ILotsAcceptedMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID)
@lbr_view_config(context=ILotsElectedMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID)
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
        result = True
        for op in order.ordered_products:
            for opi in op.ordered_product_items:
                result = result and opi.tokens
        return result

    def refresh(self, request, order):
        # XXX: 座席番号などが変わっている可能性があるので、何かすべきような...
        pass

    def cancel(self, request, order):
        # キャンセルフラグを立てるべきだと思うけど...
        pass

    def refund(self, request, order, refund_record):
        pass

    def get_order_info(self, request, order):
        return {}
