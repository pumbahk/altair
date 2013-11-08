# -*- coding:utf-8 -*-

from pyramid.view import view_config
from altair.mobile import mobile_view_config
from altair.app.ticketing.payments.interfaces import IOrderDelivery
from altair.app.ticketing.cart.interfaces import ICartDelivery
from altair.app.ticketing.mails.interfaces import ICompleteMailDelivery, IOrderCancelMailDelivery
from altair.app.ticketing.mails.interfaces import ILotsAcceptedMailDelivery
from altair.app.ticketing.mails.interfaces import ILotsElectedMailDelivery
from altair.app.ticketing.mails.interfaces import ILotsRejectedMailDelivery

from . import models as m
from altair.app.ticketing.core import models as core_models
from . import logger
import qrcode
import StringIO
from pyramid.response import Response
from altair.app.ticketing.qr import qr
from altair.app.ticketing.cart import helpers as cart_helper
from altair.app.ticketing.core import models as c_models
from collections import namedtuple

from . import QR_DELIVERY_PLUGIN_ID as DELIVERY_PLUGIN_ID

def includeme(config):
    config.add_delivery_plugin(QRTicketDeliveryPlugin(), DELIVERY_PLUGIN_ID)
    config.scan(__name__)

def _overridable(path):
    from . import _template
    if _template is None:
        return '%s:templates/%s' % (__name__, path)
    else:
        return _template(path, type='overridable', for_='payments', plugin_type='delivery', plugin_id=DELIVERY_PLUGIN_ID)

@view_config(context=ICartDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer=_overridable("qr_confirm.html"))
def deliver_confirm_viewlet(context, request):
    return dict()

QRTicket = namedtuple("QRTicket", "order performance product seat token printed_at")

@view_config(context=IOrderDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer=_overridable("qr_complete.html"))
@mobile_view_config(context=IOrderDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer=_overridable("qr_complete_mobile.html"))
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

@view_config(context=ICompleteMailDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer=_overridable("qr_mail_complete.html"))
def deliver_completion_mail_viewlet(context, request):
    shipping_address = context.order.shipping_address
    return dict(h=cart_helper, shipping_address=shipping_address, 
                notice=context.mail_data("notice")
                )

@view_config(context=IOrderCancelMailDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID)
@view_config(context=ILotsRejectedMailDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID)
@view_config(context=ILotsAcceptedMailDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID)
@view_config(context=ILotsElectedMailDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID)
def delivery_notice_viewlet(context, request):
    return Response(text=u"＜QRでのお受取りの方＞\n{0}".format(context.mail_data("notice")))

class QRTicketDeliveryPlugin(object):
    def prepare(self, request, cart):
        """ 前処理 """

    def finish(self, request, cart):
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
        # 座席番号などが変わっている可能性があるので、何かすべきような...
        pass
