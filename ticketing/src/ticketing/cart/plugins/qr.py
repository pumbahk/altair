# -*- coding:utf-8 -*-

from pyramid.view import view_config
from ticketing.mobile import mobile_view_config
from ..interfaces import IOrderDelivery, ICartDelivery, ICompleteMailDelivery, IOrderCancelMailDelivery
from . import models as m
from ticketing.core import models as core_models
from . import logger
import qrcode
import StringIO
from pyramid.response import Response
from ticketing.qr import qr
from ticketing.cart import helpers as cart_helper
from ticketing.core import models as c_models
from collections import namedtuple
DELIVERY_PLUGIN_ID = 4

def includeme(config):
    config.add_delivery_plugin(QRTicketDeliveryPlugin(), DELIVERY_PLUGIN_ID)
    config.scan(__name__)

@view_config(context=ICartDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer="ticketing.cart.plugins:templates/qr_confirm.html")
def deliver_confirm_viewlet(context, request):
    return dict()

builder = qr()
builder.key = u"THISISIMPORTANTSECRET"

@view_config(context=IOrderDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer="ticketing.cart.plugins:templates/qr_complete.html")
@mobile_view_config(context=IOrderDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer="ticketing.cart.plugins:templates/qr_complete_mobile.html")
def deliver_completion_viewlet(context, request):
    tickets = [ ]
    order = context.order
    for op in order.ordered_products:
        for opi in op.ordered_product_items:
            for t in opi.tokens:
                history = core_models.TicketPrintHistory.filter_by(ordered_product_item_id = opi.id,
                                                                   seat_id = t.seat_id,
                                                                   item_token_id=t.id).first()
                class QRTicket:
                    order = context.order
                    performance = context.order.performance
                    product = op.product
                    seat = t.seat
                    token = t
                    printed_at = token.issued_at
                ticket = QRTicket()
                tickets.append(ticket)
    
    # TODO: orderreviewから呼ばれた場合とcartの完了画面で呼ばれた場合で
    # 処理を分岐したい
    
    return dict(
        paid = (order.paid_at != None),
        order = order,
        tel = order.shipping_address.tel_1,
        tickets = tickets,
        )

@view_config(context=ICompleteMailDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer="ticketing.cart.plugins:templates/qr_mail_complete.html")
def deliver_completion_mail_viewlet(context, request):
    shipping_address = context.order.shipping_address
    return dict(h=cart_helper, shipping_address=shipping_address, 
                notice=context.mail_data("notice")
                )

@view_config(context=IOrderCancelMailDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID)
def delivery_cancel_mail_viewlet(context, request):
    return Response(context.mail_data("notice"))

def _with_serial_and_seat(ordered_product,  ordered_product_item):
    if ordered_product_item.seats:
        for i, s in enumerate(ordered_product_item.seats):
            yield i, s
    else:
        for i in xrange(ordered_product.quantity):
            yield i, None

class QRTicketDeliveryPlugin(object):
    def prepare(self, request, cart):
        """ 前処理 """

    def finish(self, request, cart):
        """ 確定時処理 """
        order = cart.order
        for op in order.ordered_products:
            for opi in op.ordered_product_items:
                for i, seat in _with_serial_and_seat(op, opi):
                    token = core_models.OrderedProductItemToken(
                        item = opi, 
                        serial = i, 
                        seat = seat, 
                        valid=True
                        )
                    opi.tokens.append(token)
